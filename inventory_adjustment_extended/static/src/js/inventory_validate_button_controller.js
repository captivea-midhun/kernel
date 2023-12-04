odoo.define('inventory_adjustment_extended.inventory_validate_button_controller', function (require) {
    "use strict";

    var InventoryValidationController = require('stock.InventoryValidationController');
    var Dialog = require('web.Dialog');
    var core = require('web.core');
    var ajax = require('web.ajax');
    var _t = core._t;
    var qweb = core.qweb;
    var _super_InventoryValidationController = InventoryValidationController.prototype;

    InventoryValidationController.include({

        _confirmInventory: function() {

            var self = this;
            var prom = Promise.resolve();
            var recordID = this.renderer.getEditableRecordID();
            if (recordID) {
                prom = this.saveRecord(recordID);
            }

            prom.then(function () {
                self._rpc({
                    model: 'stock.inventory',
                    method: 'action_validate',
                    args: [self.inventory_id]
                }).then(function (res) {
                    var exitCallback = function (infos) {
                        if (infos && infos.special) {
                            return;
                        }
                        self.do_notify(
                            _t("Success"),
                            _t("The inventory has been validated"));
                        self.trigger_up('history_back');
                    };

                    if (_.isObject(res)) {
                        self.do_action(res, { on_close: exitCallback });
                    } else {
                        return exitCallback();
                    }
                });
            });
        },

        _onValidateInventory: function () {

            var self = this;
            Dialog.confirm(this,
                _t("You're about to complete and validate your inventory count. Do you wish to proceed?"), {
                   confirm_callback: function () {
                        self._confirmInventory()
                   },
                });
            },
    });
});