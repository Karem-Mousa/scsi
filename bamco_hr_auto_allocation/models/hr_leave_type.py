from odoo import models, fields, api, _
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError, AccessError
from odoo import models, fields, api, _
from odoo.http import request
import base64

from odoo.exceptions import Warning as UserError
import re

# -*- coding: utf-8 -*-

from odoo import models, fields, api
import hashlib
import json

from odoo import api, models
from odoo.http import request
from odoo import models, fields, api, _
from odoo.exceptions import UserError
from odoo.exceptions import ValidationError, AccessError
from odoo import models, fields, api, _
from odoo.http import request
from odoo.exceptions import Warning as UserError
from odoo.tools import ustr
from datetime import date, timedelta, datetime, time
from datetime import date as date_lib
import odoo
import calendar
from dateutil import rrule
from dateutil.relativedelta import relativedelta
from odoo.tools.float_utils import float_round
from odoo.addons.resource.models.resource import float_to_time, HOURS_PER_DAY


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    required_attachment = fields.Boolean()
    submit_after = fields.Integer("Allow Submitting After Request Date By Days", required=True,
                                  default=-1)
    submit_before = fields.Integer("Allow Submitting Before Request Date By Days", required=True,
                                   default=-1)
    submit_5days_before = fields.Integer("Allow Submitting (5 Days Or More) Before Request Date By Days", required=True,
                                         default=-1)
    # consecutive_days_per_month = fields.Integer("Maximum Num Consecutive Days Per Month", required=True,
    #                                             default=-1)
    # not_allowed_consecutive_types = fields.Many2many('hr.leave.type', 'source_type', 'destination_type',
    #                                                  'source_destination_leave_type', domain="[('id','!=',id)]")
    hr_validation = fields.Boolean("HR Validation")

    # work_from_home = fields.Boolean("Is Work From Home")

    maternity_leave = fields.Boolean()
    compassionate_leave = fields.Boolean()
    pilgrimage_leave = fields.Boolean()
    consume_weekends = fields.Boolean()
    military_service = fields.Boolean()
    annual_leave = fields.Boolean()
    casual_leave = fields.Boolean()
    marriage_leave = fields.Boolean()
    days_off = fields.Boolean()
    create_calendar_meeting = fields.Boolean(string="Display Time Off in Calendar", default=False)

    # def name_get(self):
    #     if not self._context.get('employee_id'):
    #         # leave counts is based on employee_id, would be inaccurate if not based on correct employee
    #         return super(HrleaveType, self).name_get()
    #     res = []
    #     for record in self:
    #         name = record.name
    #         if record.requires_allocation == "yes":
    #             name = "%(name)s (%(count)s)" % {
    #                 'name': name,
    #                 'count': _('%g remaining out of %g') % (
    #                     float_round(record.remain_leaves, precision_digits=2) or 0.0,
    #                     float_round(record.taken_alloc, precision_digits=2) or 0.0,
    #                 ) + (_(' hours') if record.request_unit == 'hour' else _(' days'))
    #             }
    #         res.append((record.id, name))
    #     return res

    # taken_alloc = fields.Float(
    #     compute='_compute_leaves')
    #
    # taken_leaves = fields.Float(
    #     compute='_compute_leaves')
    #
    # remain_leaves = fields.Float(
    #     compute='_compute_leaves')

    # @api.depends_context('employee_id', 'default_employee_id')
    # def _compute_leaves(self):
    #     data_days = {}
    #     employee_id = self._get_contextual_employee_id()
    #
    #     if employee_id:
    #         data_days = (self.get_employees_days(employee_id)[employee_id[0]] if isinstance(employee_id, list) else
    #                      self.get_employees_days([employee_id])[employee_id])
    #
    #     for holiday_status in self:
    #         result = data_days.get(holiday_status.id, {})
    #         holiday_status.max_leaves = result.get('max_leaves', 0)
    #         holiday_status.leaves_taken = result.get('leaves_taken', 0)
    #         holiday_status.remaining_leaves = result.get('remaining_leaves', 0)
    #         holiday_status.virtual_remaining_leaves = result.get('virtual_remaining_leaves', 0)
    #         holiday_status.virtual_leaves_taken = result.get('virtual_leaves_taken', 0)
    #         holiday_status.taken_alloc = result.get('taken_alloc', 0)
    #         holiday_status.taken_leaves = result.get('taken_leaves', 0)
    #         holiday_status.remain_leaves = holiday_status.taken_alloc - holiday_status.taken_leaves

    # def get_employees_days(self, employee_ids, date=None):
    #     if not date:
    #         allocation_date = self.env.context.get('default_date_from', fields.Date.context_today(self))
    #         if not allocation_date:
    #             date = fields.Date.context_today(self)
    #         else:
    #             date = allocation_date
    #         date = fields.Date.to_date(str(date))
    #     result = super(HrleaveType, self).get_employees_days(employee_ids, date)
    #     for employee in result.keys():
    #         for type in result[employee].keys():
    #             requests = self.env['hr.leave'].search([
    #                 ('employee_id', 'in', [employee]),
    #                 ('state', 'in', ['confirm', 'validate1', 'validate']),
    #                 ('holiday_status_id', 'in', [type])
    #             ])
    #             print(date)
    #             allocations = self.env['hr.leave.allocation'].search([
    #                 ('employee_id', 'in', [employee]),
    #                 ('state', 'in', ['confirm', 'validate1', 'validate']),
    #                 ('holiday_status_id', 'in', [type]),
    #                 ('date_from', '<=', date),
    #                 '|', ('date_to', '=', False),
    #                 ('date_to', '>=', date),
    #             ])
    #             print(allocations)
    #             taken_leaves = 0
    #
    #             for request in requests:
    #                 if not request.holiday_allocation_id or request.holiday_allocation_id in allocations:
    #                     taken_leaves += (request.number_of_hours_display
    #                                      if request.leave_type_request_unit == 'hour'
    #                                      else request.number_of_days)
    #             taken_alloc = 0
    #
    #             for allocation in allocations.sudo():
    #                 if allocation.state == 'validate' and allocation.holiday_status_id.requires_allocation == 'yes':
    #                     all_allocation = 0
    #                     all_allocation += (allocation.number_of_hours_display
    #                                        if allocation.type_request_unit == 'hour'
    #                                        else allocation.number_of_days)
    #                     if not allocation.is_remaining:
    #                         if allocation.date_to:
    #                             date_difference = relativedelta(allocation.date_to, allocation.date_from)
    #                             plus_days = 1
    #                             day_end_date = allocation.date_to.day
    #                             if day_end_date == 31:
    #                                 plus_days += -1
    #                             elif day_end_date == 29:
    #                                 plus_days += 1
    #                             elif day_end_date == 28:
    #                                 plus_days += 2
    #                             months = date_difference.months + ((date_difference.days + plus_days) / 30)
    #                             days_per_month = all_allocation / months
    #                             date_difference = relativedelta(date_lib(date_lib.today().year, date_lib.today().month,
    #                                                                      calendar.monthrange(
    #                                                                          date_lib.today().year,
    #                                                                          date_lib.today().month)[1]),
    #                                                             allocation.date_from)
    #                             plus_days = 1
    #                             day_end_date = date_lib(date_lib.today().year, date_lib.today().month,
    #                                                     calendar.monthrange(
    #                                                         date_lib.today().year,
    #                                                         date_lib.today().month)[1]).day
    #                             if day_end_date == 31:
    #                                 plus_days += -1
    #                             elif day_end_date == 29:
    #                                 plus_days += 1
    #                             elif day_end_date == 28:
    #                                 plus_days += 2
    #                             months = date_difference.months + ((date_difference.days + plus_days) / 30)
    #                             taken_alloc += months * days_per_month
    #                         else:
    #                             date_difference = relativedelta(date_lib(allocation.date_from.year, 12, 31),
    #                                                             allocation.date_from)
    #                             months = date_difference.months + ((date_difference.days) / 30)
    #                             days_per_month = all_allocation / months
    #                             date_difference = relativedelta(date_lib(date_lib.today().year, date_lib.today().month,
    #                                                                      calendar.monthrange(
    #                                                                          date_lib.today().year,
    #                                                                          date_lib.today().month)[1]),
    #                                                             allocation.date_from)
    #                             plus_days = 1
    #                             day_end_date = date_lib(date_lib.today().year, date_lib.today().month,
    #                                                     calendar.monthrange(
    #                                                         date_lib.today().year,
    #                                                         date_lib.today().month)[1]).day
    #                             if day_end_date == 31:
    #                                 plus_days += -1
    #                             elif day_end_date == 29:
    #                                 plus_days += 1
    #                             elif day_end_date == 28:
    #                                 plus_days += 2
    #                             months = date_difference.months + ((date_difference.days + plus_days) / 30)
    #                             taken_alloc += months * days_per_month
    #                     else:
    #                         taken_alloc += all_allocation
    #
    #             result[employee][type]['taken_leaves'] = taken_leaves
    #             result[employee][type]['taken_alloc'] = taken_alloc
    #
    #     return result

    def name_get(self):
        if not self._context.get('employee_id'):
            # leave counts is based on employee_id, would be inaccurate if not based on correct employee
            return super(HrLeaveType, self).name_get()
        res = []
        for record in self:
            name = record.name
            if record.requires_allocation == "yes":
                name = "%(name)s (%(count)s)" % {
                    'name': name,
                    'count': _('%g remaining out of %g') % (
                        float_round(record.virtual_remaining_leaves, precision_digits=2) or 0.0,
                        float_round(record.max_leaves, precision_digits=2) or 0.0,
                    ) + (_(' hours') if record.request_unit == 'hour' else _(' days'))
                }
            res.append((record.id, name))
        return res

    def _default_year(self):
        today = datetime.today()
        current_year = today.year
        return str(current_year)

    def _get_year_selection(self):
        _year_selection = [(str(2015), str(2015)), (str(2016), str(2016)), (str(2017), str(2017))]
        today = datetime.today()
        current_year = today.year
        year = 2018
        # year = current_year + 1
        while year <= current_year + 1:
            _year_selection.append((str(year), str(year)))
            year += 1
        return _year_selection

    auto_allocation = fields.Boolean('Automatic Allocation')
    allocation_year = fields.Selection(string="Year", selection=_get_year_selection, default=_default_year,
                                       required=False, )

    depend_on_age = fields.Boolean("Depends On Age And Insurance ")
    number_of_days = fields.Float('Number Of Days')
    number_of_days_more_than_50_year = fields.Float('Number Of Days For > 50')
    number_of_days_less_than_50_year = fields.Float('Number Of Days For < 50')
