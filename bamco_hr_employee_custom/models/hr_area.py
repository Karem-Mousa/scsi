# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HRArea(models.Model):
    _name = 'hr.area'

    name = fields.Char('القسم')
    # analytic_account_id = fields.Many2one('account.analytic.account' )
