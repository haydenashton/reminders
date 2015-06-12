$(function(){

   // Enables Mustache.js-like templating.
   _.templateSettings = {
      interpolate : /\{\{(.+?)\}\}/g,
      evaluate : /\{\[([\s\S]+?)\]\}/g
   };


  Reminder = Backbone.Model.extend({
    defaults: {
        title: "",
        description: "",
        user_id: "",
        reminder_time: "01/01/2015 00:00",
        reminder_deleted: false,
        reminder_sent: false,
        created: ""
    },
      url: "/reminders"
  });

  ReminderList = Backbone.Collection.extend({
    url : "/reminders",
    model : Reminder,
    //comparator: "created"
    comparator: function(arg){
        return Date.parse(arg.get('created'));
    }
  });


  // Represents a reminder entry
  var ReminderEntryView = Backbone.View.extend({
    tagName : "div",
    className: "reminder-entry",
    template : _.template($("#reminder-entry-template").html()),
    events : {
      "click .cancel": "cancelReminder"
    },
    // If there's a change in our model, re-render it
    initialize : function(){
      this.model.bind('change', this.render, this);
    },

    render : function(){
      var content = this.model.toJSON();
      $(this.el).html(this.template(content));
      return this;
    },

    cancelReminder: function(){
      var self = this;
      this.model.set("reminder_deleted", true);
      this.model.save({}, {success: function(){
        self.remove();
      }});
    }
  });


  // Represents a reminder entry
  var ReminderAddView = Backbone.View.extend({
    tagName : "div",
    template : _.template($("#reminder-add-template").html()),
    events : {
      'click #create-reminder': 'createReminder',
      'change .reminder-field': 'setReminderValue',
      'change .time-part-field': 'setDateTime'
    },

    render : function(){
      var content = this.model.toJSON();
      $(this.el).html(this.template(content));
      return this;
    },

    createReminder: function(){
      var self = this;
      this.model.save(this.model.toJSON(), {success: function(mod){
        reminders.fetch();
        self.model = new Reminder();
      }});
    },

    setReminderValue: function(e){
      var target = $(e.currentTarget);
      var attribute = target.data("target");
      var value = target.val();
      this.model.set(attribute, value);
    },

    setDateTime: function(e){
      var element = $(e.currentTarget);
      var target = parseInt(element.data("target"));
      var value = element.val();
      var current = this.model.get("reminder_time");
      var updated = current.split(" ");
      updated[target] = value;
      this.model.set("reminder_time", updated.join(" "));
    },

    datePart: function(){
        return this.model.get("reminder_time").split(" ")[0];
    },

    timePart: function(){
        return this.model.get("reminder_time").split(" ")[1];
    }
  });


  // The view for all Reminders
  var ReminderTable = Backbone.View.extend({
    el: $("#reminder_list"),
    initialize : function(){
      _.bindAll(this, 'refreshed', 'addRow', 'deleted');
      reminders.bind("reset", this.refreshed, this);
      reminders.bind("add", this.addRow, this);
      reminders.bind("remove", this.deleted, this);
    },
    // Prepends an entry row
    addRow : function(reminder){
      var self = this;
      var view = new ReminderEntryView({model: reminder});
      var rendered = view.render().el;
      $(this.el).prepend(rendered);
    },

    // Renders all reminders into the table
    refreshed : function(){
      $("#reminder_list").empty();
      if(reminders.length > 0){
        // add each element
        reminders.each(this.addRow);
      }
    },

    deleted : function(model){
      this.refreshed();
    },
    close: function(){;
      this.remove();
      this.unbind();
      reminders.unbind("reset", this.refreshed);
      reminders.unbind("add", this.addRow);
      reminders.unbind("remove", this.deleted);
    }
  });


  // The App controller initializes the app by calling `estimates.fetch()`
  var App = Backbone.Router.extend({
    initialize : function(){
      reminders.fetch();

      sync(reminders);
    }
  });


  reminders = new ReminderList();
  var view_index = new ReminderTable();
  var add_view = new ReminderAddView({model: new Reminder()});
  $("#reminder_add").html(add_view.render().el);
  $("#reminder_time").timepicker({showMeridian: false, minuteStep: 1});
  new App();

});

function sync(reminders){
    setTimeout(function(){
        //Backbone.sync("read", reminders);
        reminders.fetch();
        sync(reminders);
    }, 30000);
}