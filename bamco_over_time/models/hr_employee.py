from odoo import fields, models, api, _
from datetime import datetime, timedelta
import math

from odoo.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    overtime_state = fields.Selection([('draft','Draft'),('approved','Approved')],string='Overtime State')