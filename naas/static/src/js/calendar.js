odoo.define('naas.calendar', ['web.CalendarModel'], function (require) {
  "use strict";
  var existingCalendarModel = require('web.CalendarModel');
  existingCalendarModel.prototype._old_getFullCalendarOptions = existingCalendarModel.prototype._getFullCalendarOptions;
  existingCalendarModel.prototype._getFullCalendarOptions = function() {
    var options = this._old_getFullCalendarOptions();
    options.selectable = false;
    options.editable = false;
    options.droppable = false;
    return options;
  };
});