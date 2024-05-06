from odoo import api, fields, models


class ResCompany(models.Model):
    _inherit = 'res.company'

    header_template = fields.Binary()
    footer_template = fields.Binary()
