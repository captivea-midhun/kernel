# -*- coding: utf-8 -*-
##############################################################################
#
#    Bista Solutions Pvt. Ltd
#    Copyright (C) 2020 (https://www.bistasolutions.com)
#
##############################################################################

from odoo import models, _
from odoo.exceptions import UserError


class MrpWorkOrder(models.Model):
    _inherit = 'mrp.workorder'

    def _next(self, continue_production=False):
        if self.current_quality_check_id and \
                self.current_quality_check_id.point_id and \
                self.current_quality_check_id.point_id.team_id and \
                self.current_quality_check_id.point_id.team_id.users_ids and \
                self.env.user.id not in \
                self.current_quality_check_id.point_id.team_id.users_ids.ids:
            raise UserError(_('You have not rights to perform the next step.'))
        return super(MrpWorkOrder, self)._next(continue_production=continue_production)
