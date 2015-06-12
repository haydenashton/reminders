<%inherit file="template.mak"/>
<%block name="content">


    <div>
        <div class="fixed">
            <h1>Reminders</h1>
            <div class="well" id="reminder_add"></div>
        </div>
        <div class="well" id="reminder_list"></div>
    </div>

    <script type="text/template" id="reminder-add-template">
        <div id="add-form">
            <div class="form-group">
                <label>Title:</label>
                <input data-target="title" type="text" class="form-control input input-large reminder-field" id="reminder_title" name="title"/>
            </div>
            <div class="form-group">
                <label>Description:</label>
                <textarea data-target="description" class="form-control input input-large reminder-field" id="reminder_description" name="description"></textarea>
            </div>
            <div class="form-group">
                <label>Reminder Time:</label>
                <div>
                    <input type="text" data-target="0" data-provide="datepicker" data-container="#reminder_add" data-date-format="dd/mm/yyyy" class="form-control input time-part time-part-field" id="reminder-date" placeholder="dd/mm/yyyy" value="{{ this.datePart() }}"/>

                    <div class="time-part input-group bootstrap-timepicker">
                        <input data-target="1" style="display:inline;" type="text" class="form-control input time-part-field" id="reminder_time" placeholder="hh:mm" name="time" value="{{ this.timePart() }}" />
                        <span class="inline input-group-addon"><i class="glyphicon glyphicon-time"></i></span>
                    </div>


                    <!--<input id="timepicker1" type="text" class="input-small">-->

                </div>
            </div>

            <button type="button" class="btn btn-primary btn-large" id="create-reminder"> Create</button>
        </div>
    </script>

    <script type="text/template" id="reminder-entry-template">
        <div>
            <button type="button" class="close cancel pull-right"><span>&times;</span></button>
        </div>
        <div>
            <label>Name:</label>
            {{ title }}
        </div>
        <div>
            <label>Description:</label>
            {{ description }}
        </div>
        <div>
            <label>Reminder Time:</label>
            {{ reminder_time }}
        </div>
        <div>
            <small>Created {{ created.replace('T', ' at ') }}</small>
        </div>
    </script>

    <hr/>

</%block>

<%block name="app_includes">
    <link rel="stylesheet" href="${request.static_url('reminder:static/css/style.css')}"/>
    <link rel="stylesheet" href="${request.static_url('reminder:static/css/bootstrap-datepicker.min.css')}"/>
    <link rel="stylesheet" href="${request.static_url('reminder:static/css/bootstrap-timepicker.min.css')}"/>
    <script type="text/javascript" src="${request.static_url('reminder:static/js/lib/bootstrap-datepicker.min.js')}"></script>
    <script type="text/javascript" src="${request.static_url('reminder:static/js/lib/bootstrap-timepicker.min.js')}"></script>
    <script type="text/javascript" src="${request.static_url('reminder:static/js/app.js')}"></script>
</%block>