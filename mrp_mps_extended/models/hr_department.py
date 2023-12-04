from odoo import fields, models, api


class HRDep(models.Model):
    _inherit = 'hr.department'

    use_for_mps = fields.Boolean('Use for MPS as Manufacturing?', default=False)

    @api.model
    def create(self, vals_list):
        res = super(HRDep, self).create(vals_list)
        if res and res.use_for_mps:
            manufacturing = self.search([('id', '!=', res.id), ('use_for_mps', '=', True)])
            if manufacturing:
                manufacturing.use_for_mps = False
        return res

    def write(self, vals):
        res = super(HRDep, self).write(vals)
        if 'use_for_mps' in vals.keys() and vals['use_for_mps']:
            manufacturing = self.search([('id', '!=', self.id), ('use_for_mps', '=', True)])
            if manufacturing:
                manufacturing.use_for_mps = False
        return res
