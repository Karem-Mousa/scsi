from odoo import models, fields, api, _
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class LeaveAllocation(models.Model):
    _inherit = 'hr.leave.allocation'

    checked = fields.Boolean('checked')
    code = fields.Char(related="employee_id.attendance_id_char", store=True)
    is_remaining = fields.Boolean()
