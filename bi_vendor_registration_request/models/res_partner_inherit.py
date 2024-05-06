# -*- coding: utf-8 -*-
from odoo import models, fields, _


class EXResPartnerInherit(models.Model):
    _inherit = "res.partner"

    # x_commercial_register_number = fields.Char('Commercial Register Number')
    x_iban_number = fields.Char("IBAN Number")

    x_commercial_register = fields.Image(string='Commercial Register')
    x_commercial_register_date = fields.Date(string='Commercial Register Date')
    x_commercial_register_num = fields.Char(string='Commercial Register Number')

    x_commercial_chamber_certificate = fields.Image(string='Commercial Chamber Certificate')
    x_commercial_chamber_certificate_date = fields.Date(string='Commercial Chamber Certificate Date')
    x_commercial_chamber_certificate_num = fields.Char(string='Commercial Chamber Certificate Number')

    x_zakat_certificate = fields.Image(string='Zakat Certificate')
    x_zakat_certificate_date = fields.Date(string='Zakat Certificate Date')
    x_zakat_certificate_num = fields.Char(string='Zakat Certificate Number')

    x_social_insurance_certificate = fields.Image(string='Social Insurance Certificate')
    x_social_insurance_certificate_date = fields.Date(string='Social Insurance Certificate Date')
    x_social_insurance_certificate_num = fields.Char(string='Social Insurance Certificate Number')

    x_saudization_certificate = fields.Image(string='Saudization Certificate')
    x_saudization_certificate_date = fields.Date(string='Saudization Certificate Date')
    x_saudization_certificate_num = fields.Char(string='Saudization Certificate Number')

    x_tax_certificate = fields.Image(string='Tax Certificate')
    x_iban_certificate = fields.Image(string='IBAN Certificate')
    x_iban_bank = fields.Many2one('excellence.bank')
