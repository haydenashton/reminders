from datetime import datetime
import threading
from multiprocessing import Queue
from multiprocessing.queues import Empty

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.interval import IntervalTrigger

import transaction

from models import Reminder, DBSession

from remindertypes import EmailReminder


class MyScheduler(object):

    def __init__(self, settings):
        self.scheduler = BackgroundScheduler()
        self.reminder_types = [EmailReminder, ]
        self.settings = settings
        self.create_job()

    def create_job(self):
        self.scheduler.add_job(handle_reminders,
                               trigger=IntervalTrigger(minutes=1),
                               args=(self.reminder_types, self.settings)
        )

    def start(self):
        """
        Start the scheduler.
        :return:None
        """
        self.scheduler.start()


    def add_reminder_type(self, reminder_type):
        """
        Add a reminder strategy to use when sending reminders.
        :param reminder_type: reminder duck type
        :return: None
        """
        self.reminder_types.append(reminder_type)


def handle_reminders(reminder_types, settings):
    """
    Job to send reminders. Runs every minute.
    :return: None
    """
    print "Running job"
    # Get all reminders that have not been sent or cancelled
    reminders = DBSession.query(Reminder).filter((Reminder.reminder_sent == False) &
                                                 (Reminder.reminder_deleted == False) &
                                                 (Reminder.reminder_time < datetime.now())).all()

    queue = Queue()
    threads = create_reminder_threads(reminders, reminder_types, queue, settings)

    # Wait for all threads to complete then process results in one go
    for thrd in threads:
        thrd.join()

    results = get_results(queue)
    process_results(reminders, results)


def create_reminder_threads(reminders, reminder_types, queue, settings):
    """
    Create one thread per reminder that needs to be sent
    :param reminders: list of reminders to process
    :param queue: Queue thread safe queue to store results
    :return: list Threads created for reminders
    """
    threads = []
    lock = threading.Lock()
    for reminder in reminders:
        # Create new threads. SQLite objects can only be used in thread they were created in so use dictionary values
        thrd = threading.Thread(target=send_reminder, args=(reminder.as_dict(),
                                                            reminder.user.as_dict(),
                                                            reminder_types,
                                                            queue, lock,
                                                            settings))
        thrd.start()
        threads.append(thrd)

    return threads


def get_results(queue):
    """
    Get the results from the queue
    :param queue: Queue to pull results from
    :return: list results
    """
    results = []
    for i in range(queue.qsize()):
        try:
            result = queue.get(timeout=5)
        except Empty:
            result = False

        results.append(result)
    return results


def process_results(reminders, results):
    """
    Update reminders in db based on the results
    :param reminders: list reminders to be updated
    :param results: list results to process
    :return: None
    """
    for reminder in reminders:
        for result in results:
            if result[1] and reminder.id == result[0]:
                print "Setting %s to true" % reminder.id
                reminder.reminder_sent = result[1]
                DBSession.add(reminder)
            elif not result[1]:
                print "Failed to send reminder:", reminder.id

    transaction.commit()


def send_reminder(reminder, user, reminder_types, queue, lock, settings):
    """
    Send reminder to user using all registered strategies.
    :param reminder: dict representation of the reminder
    :param user: dict representation of the user
    :param queue: Queue to store results
    :param lock: Lock
    :return: None
    """
    result = False
    with lock:
        print "Sending reminder:", reminder['id']

        # As long as reminder strategy succeeds return true
        for reminder_type in reminder_types:
            try:
                rt = reminder_type({'reminder': reminder, 'user': user, 'settings': settings})
                rt.send_reminder()
                result = True
                print "Sent reminder: %s" % reminder['id']
            except Exception, e:
                print e
                print "Could not send reminder using %s for %s", (repr(reminder_type), reminder['id'])

        queue.put((reminder['id'], result))
