# -*- coding: utf-8 -*-

from odoo import models, fields, api


class hr_salary_rule_inheri(models.Model):
    _inherit = 'hr.salary.rule'

    shared_between_structures = fields.Boolean('Shared Between Structures')
    shared_structure = fields.Many2many('hr.payroll.structure', string='Shared Structures')
