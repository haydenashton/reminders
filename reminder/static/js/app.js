$(function(){

   // Enables Mustache.js-like templating.
   _.templateSettings = {
      interpolate : /\{\{(.+?)\}\}/g,
      evaluate : /\{\[([\s\S]+?)\]\}/g
   };


  Reminder = Backbone.Model.extend({
    defaults: function(){
      var today = moment().format("DD/MM/YYYYTHH:mm");
      return {
          title: "",
          description: "",
          user_id: "",
          reminder_time: today,
          reminder_deleted: false,
          reminder_sent: false,
          created: ""
      };
    },
    url: "/reminders",

    getSplitDate: function(){
      return this.get("reminder_time").split("T");
    },

    getDate: function(){
        return this.getSplitDate()[0];
    },

    getTime: function(){
      return this.getSplitDate()[1];
    },

    setDate: function(value){
      var current = this.getSplitDate();
      current[0] = value;
      this.set("reminder_time", current.join("T"));
    },

    setTime: function(value){
      var current = this.getSplitDate();
      current[1] = value;
      this.set("reminder_time", current.join("T"));
    }
  });

  ReminderList = Backbone.Collection.extend({
    url : "/reminders",
    model : Reminder,

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

    show: function(){
      $("#reminder_add").html(this.render().el);
      $("#reminder_time").timepicker({showMeridian: false, minuteStep: 1});
      $("#reminder-date").datepicker({container: "#date_time"});
    },

    render: function(){
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

      // Index in date string
      var target = element.data("target");
      var value = element.val();

      if(target === "date"){
        this.model.setDate(value);
      }
      else {
        this.model.setTime(value);
      }
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
  add_view.show();
  new App();

});

function sync(reminders){
    setTimeout(function(){
        //Backbone.sync("read", reminders);
        reminders.fetch();
        sync(reminders);
    }, 30000);
}
