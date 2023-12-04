# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, api, tools


class IrModelAccess(models.Model):
    _inherit = 'ir.model.access'

    @api.model
    @tools.ormcache_context('self._uid', 'model', 'mode', 'raise_exception',
                            keys=('lang',))
    def check(self, model, mode='read', raise_exception=True):
        """Override method to maintenance user can reassign the equipments."""
        context = dict(self.env.context)
        user_id = self.env.user
        if not user_id.has_group('maintenance.group_equipment_manager') \
                and mode != 'read' and model == 'maintenance.equipment':
            return False
        return super(IrModelAccess, self).check(
            model, mode, raise_exception=raise_exception)
