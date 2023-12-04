odoo.define('stock_traceability.ReportWidget', function (require) {'use strict';

var ReportWidget = require('stock.ReportWidget');
var Dialog = require('web.Dialog');
var core = require('web.core');
var QWeb = core.qweb;

ReportWidget.include({
    events: _.extend({}, ReportWidget.prototype.events, {
        'click #expand_stock_lines': 'actionExpandAll',
    }),

    actionOpenLot: function (ev) {
        var self = this;
        ev.preventDefault();
        // Check if the logged in user is a manufacturing manager
        this.getSession().user_has_group('mrp.group_mrp_manager').then(function(has_group) {
            if (has_group) {
                var $el = $(ev.currentTarget);
                // return if not virtual location
                if (!$el.hasClass('bs_traceability_update')) {
                    return;
                }
                var $tr = $el.parents('tr');
                var $trData = $tr.data();
                var $input = $('<input>').attr('value', $trData.lot_name).val($trData.lot_name);
                // replace with the input field for editable
                $el.replaceWith($input);
                $input.focus();
                $input.on('focusout', function (e) {
                    $(this).replaceWith($el);
                    if ($trData.lot_name !== this.value) {
                        $tr.addClass('text-danger');
                        // check if nwelly added lot is available for this product or not
                        //  if yes update or raise the warning
                        return self._rpc({
                            method: 'mrp_update_lot_serial',
                            model: 'stock.move.line',
                            args: [$trData.model_id, this.value],
                        }).then(function (result) {
                            if (result && result.new_lot_id) {
                                // update new lot id for the line
                                $tr.find('td').data('lot_name', result.new_lot_name)
                                    .addClass('text-success')
                                    .removeClass('text-danger');
                                $tr.data({
                                    'lot_name': result.new_lot_name,
                                    'lot_id': result.new_lot_id,
                                });
                                $el.html(result.new_lot_name);
                            }
                        })
                    }
                })
            }
        });
    },
    actionExpandAll: function (ev) {
        var $el = $(ev.currentTarget);
        if ($el.hasClass('fa-expand')) {
            this.bs_expand_all = true;
            this._expandAllLines();
        } else if ($el.hasClass('fa-compress')) {
            this._compressAllLines();
        }
        $el.toggleClass('fa-expand', !this.bs_expand_all)
        $el.toggleClass('fa-compress', this.bs_expand_all)
    },
    autounfold: function(target, lot_name) {
        var self = this;
        var $CurretElement;
        $CurretElement = $(target).parents('tr').find('td.o_stock_reports_unfoldable');
        var active_id = $CurretElement.data('id');
        var active_model_name = $CurretElement.data('model');
        var active_model_id = $CurretElement.data('model_id');
        var row_level = $CurretElement.data('level');
        var $cursor = $(target).parents('tr');
        this._rpc({
                model: 'stock.traceability.report',
                method: 'get_lines',
                args: [parseInt(active_id, 10)],
                kwargs: {
                    'model_id': active_model_id,
                    'model_name': active_model_name,
                    'level': parseInt(row_level) + 30 || 1
                },
            })
            .then(function (lines) {// After loading the line
                _.each(lines, function (line) { // Render each line
                    $cursor.after(QWeb.render("kernel_stock_traceability.report_mrp_line", {l: line}));
                    $cursor = $cursor.next();
                    if (($cursor && line.unfoldable && line.lot_name == lot_name) || (line.unfoldable && self.bs_expand_all)) {
                        self.autounfold($cursor.find(".fa-caret-right"), lot_name);
                    } else if (self.$('.o_stock_reports_unfoldable.o_stock_reports_caret_icon .fa-caret-right').length === 0) {
                        // set false to stop the functionality on normal click of the caret sign
                        self.bs_expand_all = false;
                    }
                });
            });
        $CurretElement.attr('class', 'o_stock_reports_foldable ' + active_id); // Change the class, and rendering of the unfolded line
        $(target).parents('tr').find('span.o_stock_reports_unfoldable').replaceWith(QWeb.render("foldable", {lineId: active_id}));
        $(target).parents('tr').toggleClass('o_stock_reports_unfolded');
    },
    _compressAllLines: function () {
        this.$('.o_stock_reports_foldable.o_stock_reports_caret_icon').click();
    },
    _expandAllLines: function () {
        if (this.bs_expand_all) {
            var self = this;
            var def = _.each(this.$('.o_stock_reports_unfoldable.o_stock_reports_caret_icon .fa-caret-right'), function (el) {
                self.bs_expand_all = true;
                self.autounfold($(el));
            });
        }
    }
})
return ReportWidget;
});
