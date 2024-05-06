from odoo import fields, api, models, _
from odoo import exceptions

from datetime import datetime, time

from dateutil import rrule


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'

    is_analytic = fields.Boolean('Is Analytic')
