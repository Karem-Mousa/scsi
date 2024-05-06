from odoo import fields, models, api, _

import pytz
from dateutil.relativedelta import relativedelta


class HrAttendance(models.Model):
    _inherit = "hr.attendance"

    x_arabic_name = fields.Char(related='employee_id.arabic_name')
