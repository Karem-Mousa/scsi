from email.policy import default

from odoo import fields, models, api, _


class HrSalaryRule(models.Model):
    _inherit = "hr.salary.rule"

    x_show_partner = fields.Boolean(string="Show partner")

