from odoo import fields, models, api, _

import pytz
from dateutil.relativedelta import relativedelta


class HrLeaveType(models.Model):
    _inherit = "hr.leave.type"

    is_emergency_leave = fields.Boolean()
    is_annual_leave = fields.Boolean()
