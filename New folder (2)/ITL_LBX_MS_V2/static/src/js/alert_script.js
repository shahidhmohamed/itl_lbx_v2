odoo.define("your_module_name.custom_script", function (require) {
  "use strict";

  var core = require("web.core");
  var Notification = require("web.Notification");
  var _t = core._t;

  var ListController = require("web.ListController");

  ListController.include({
    renderButtons: function ($node) {
      this._super.apply(this, arguments);

      var self = this;
      var records = this.model.get(this.handle, { raw: true });

      if (records.length > 0) {
        new Notification(self, {
          title: _t("Success"),
          message: _t("Data is present in the tree view."),
          type: "success",
          sticky: false,
        }).appendTo($node);
      }
    },
  });
});
