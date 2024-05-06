
from odoo.exceptions import ValidationError

from dateutil import relativedelta

from odoo import models, fields, api, _
from odoo.http import request
from datetime import datetime, date
from collections import defaultdict
import pytz
from odoo.addons.resource.models.resource import datetime_to_string, string_to_datetime, Intervals



class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    iqama_end_date = fields.Date('Iqama End Date')
    bank_number = fields.Char('Bank Number')
    # bank_name = fields.Char('Bank Name')
    bank_name = fields.Many2one(
        comodel_name='bank',
        string='Bank Name',
        required=False)



