from odoo.exceptions import UserError

from dateutil import relativedelta

from odoo import models, fields, api, _
from odoo.http import request
from datetime import datetime, date
from collections import defaultdict
import pytz
from odoo.addons.resource.models.resource import datetime_to_string, string_to_datetime, Intervals


class HrContract(models.Model):
    _inherit = 'hr.contract'

    basic_before = fields.Float('Basic Before', store=True)
    house_allowance_before = fields.Float('House Allowance Before', store=True)
    transportation_allowance_before = fields.Float('Transportation Allowance Before', store=True)
    other_allowance_before = fields.Float('Other Allowance Before', store=True)
    date_raise = fields.Date('Date Raise', store=True)

    @api.onchange('wage')
    def add_old_wage(self):
        for rec in self:
            if rec.wage:
                old_wage = rec._origin.wage
                rec.basic_before = old_wage
                rec.date_raise = date.today()

    @api.onchange('house_allowance')
    def add_old_house_allowance(self):
        for rec in self:
            if rec.house_allowance:
                old_house_allowance = rec._origin.house_allowance
                rec.house_allowance_before = old_house_allowance

    @api.onchange('transportation_allowance')
    def add_old_transportation_allowance(self):
        for rec in self:
            if rec.transportation_allowance:
                old_transportation_allowance_before = rec._origin.transportation_allowance
                rec.transportation_allowance_before = old_transportation_allowance_before

    @api.onchange('other_allowance')
    def add_old_other_allowance(self):
        for rec in self:
            if rec.other_allowance:
                old_other_allowance = rec._origin.other_allowance
                rec.other_allowance_before = old_other_allowance
