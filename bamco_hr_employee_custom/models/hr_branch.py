# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HRBranch(models.Model):
    _name = 'hr.branch'

    name = fields.Char('الفرع')
    analytic_account_id = fields.Many2one('account.analytic.account')
