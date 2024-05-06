from odoo import fields, models, api, _

import pytz
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    x_employee_relations = fields.One2many('excel.employee.relations', 'employee_id')
