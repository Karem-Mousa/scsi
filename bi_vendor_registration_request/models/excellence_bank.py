from odoo import fields, models, api


class ExcellenceBank(models.Model):
    _name = 'excellence.bank'
    _description = 'Description'

    name = fields.Char()
