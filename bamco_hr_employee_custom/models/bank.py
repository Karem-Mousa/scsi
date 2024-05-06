from odoo import api, fields, models


class BankDetails(models.Model):
    _name = 'bank'
    _rec_name = "name"

    name = fields.Char(
        string='Bank Name',
        required=False)
