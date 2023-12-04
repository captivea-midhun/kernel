from odoo import fields, models, api


class Emoji(models.Model):
    _name = 'emoji.logo'

    name = fields.Char()
    logo = fields.Char('Emoji')

    def name_get(self):
        return [(emoji.id, emoji.name + ' - ' + emoji.logo) for emoji in self]

    @api.model
    def name_search(self, name='', args=None, operator='ilike', limit=100):
        domain = ['|', ('name', 'like', name), ('logo', 'like', name)]
        res = self.search(domain)
        if res:
            return res.name_get()
        return super(Emoji, self).name_search(
                name=name, args=args, operator=operator, limit=limit)



class ProCat(models.Model):
    _inherit = 'product.category'

    category_emoji_id = fields.Many2one('emoji.logo')
