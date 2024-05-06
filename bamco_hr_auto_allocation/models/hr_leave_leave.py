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


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    def _validate_leave_request(self):
        for rec in self:
            rec.holiday_status_id.create_calendar_meeting = False
        super(HrLeave, self)._validate_leave_request()
        return True

    annual_days = fields.Float()
    annual_leave_id = fields.Many2one('hr.leave.type')
    attachment = fields.Binary()
    attachment_name = fields.Char()
    required_attachment = fields.Boolean(related='holiday_status_id.required_attachment')
    # work_from_home = fields.Boolean(related='holiday_status_id.work_from_home')
    maternity_leave = fields.Boolean(related='holiday_status_id.maternity_leave')
    compassionate_leave = fields.Boolean(related='holiday_status_id.compassionate_leave')
    pilgrimage_leave = fields.Boolean(related='holiday_status_id.pilgrimage_leave')
    annual_leave = fields.Boolean(related='holiday_status_id.annual_leave')
    casual_leave = fields.Boolean(related='holiday_status_id.casual_leave')
    marriage_leave = fields.Boolean(related='holiday_status_id.marriage_leave')
    days_off = fields.Boolean(related='holiday_status_id.days_off')
    # remain_days_current_months = fields.Float(compute="compute_remain_days_current_months", store=True)
    # alloc_days_current_months = fields.Float(compute="compute_remain_days_current_months", store=True)
    # leaves_days_current_months = fields.Float(compute="compute_remain_days_current_months", store=True)
    before_trial_period = fields.Boolean(copy=False)
    code = fields.Char(related="employee_id.attendance_id_char", store=True)

    @api.constrains('holiday_status_id', 'days_off', 'employee_id', 'date_from', 'annual_leave', 'casual_leave',
                    'state', 'number_of_days')
    def check_days_off(self):
        for rec in self:
            if rec.employee_id.company_id.smart_pack:
                if rec.holiday_status_id.days_off:
                    if rec.employee_id.days_off:
                        date_from = rec.date_from + timedelta(hours=2)
                        month = date_from.month
                        year = date_from.year
                        month_start = datetime(day=1, month=month, year=year, hour=0, minute=0, second=0)
                        month_end = datetime(day=calendar.monthrange(year, month)[1], month=month, year=year, hour=23,
                                             minute=59,
                                             second=59)
                        days_off_leaves = rec.env['hr.leave'].search(
                            [('employee_id', '=', rec.employee_id.id), ('days_off', '=', True),
                             ('state', '!=', 'refuse'), ('date_from', '>=', month_start),
                             ('date_from', '<=', month_end)])
                        if days_off_leaves and sum(days_off_leaves.mapped('number_of_days')) > 4:
                            raise ValidationError(_("Days Off Leave Can Be Requested only 4 Days In Month"))
                    else:
                        raise ValidationError(_("You Can Not Request Leave From This Type"))
                elif rec.holiday_status_id.annual_leave or rec.holiday_status_id.casual_leave:
                    if rec.employee_id.days_off:
                        raise ValidationError(_("You Can Not Request Annual Leave OR Casual Leave"))

    def _get_number_of_days(self, date_from, date_to, employee_id):
        if self.holiday_status_id.consume_weekends:
            diff = (self.request_date_to - self.request_date_from).days
            days = diff + 1 if not self.request_unit_half else 0.5
            hours = days * HOURS_PER_DAY
            return {'days': days, 'hours': hours}
        else:
            if employee_id:
                employee = self.env['hr.employee'].browse(employee_id)
                # We force the company in the domain as we are more than likely in a compute_sudo
                domain = [('company_id', 'in', self.env.company.ids + self.env.context.get('allowed_company_ids', []))]
                result = employee._get_work_days_data_batch(date_from, date_to, domain=domain)[employee.id]
                if self.request_unit_half and result['hours'] > 0:
                    result['days'] = 0.5
                return result

            today_hours = self.env.company.resource_calendar_id.get_work_hours_count(
                datetime.combine(date_from.date(), time.min),
                datetime.combine(date_from.date(), time.max),
                False)

            hours = self.env.company.resource_calendar_id.get_work_hours_count(date_from, date_to)
            days = hours / (today_hours or HOURS_PER_DAY) if not self.request_unit_half else 0.5
            return {'days': days, 'hours': hours}

    @api.constrains('holiday_status_id', 'number_of_days', 'maternity_leave', 'employee_id')
    def check_leaves_maternity(self):
        for rec in self:
            if rec.employee_id.company_id.ecc:
                if rec.holiday_status_id.maternity_leave:
                    if rec.number_of_days > 90:
                        raise ValidationError(_("Maternity Leave Maximum 90 Days"))
                    if rec.employee_id.hire_date:
                        ten_months = rec.employee_id.hire_date + relativedelta(months=10)
                        if date.today() <= ten_months:
                            raise ValidationError(
                                _("Maternity Leave Can Be Requested After 10 Months From Hire Date "))
                    else:
                        raise ValidationError(_("Employee Must Have Hire Date"))
                    maternity_leaves = rec.env['hr.leave'].search(
                        [('employee_id', '=', rec.employee_id.id), ('maternity_leave', '=', True),
                         ('state', '!=', 'refuse')])
                    if len(maternity_leaves) > 2:
                        raise ValidationError(_("Maternity Leave Can Be Requested only Twice"))

    @api.constrains('holiday_status_id', 'marriage_leave', 'number_of_days', 'employee_id')
    def check_leaves_marriage(self):
        for rec in self:
            if rec.employee_id.company_id.ecc:
                if rec.holiday_status_id.marriage_leave and rec.number_of_days > 5:
                    raise ValidationError(_("Marriage Leave Maximum 5 Days"))

    @api.constrains('holiday_status_id', 'annual_leave', 'casual_leave', 'employee_id', 'date_from')
    def check_leaves_annual_casual(self):
        for rec in self:
            if rec.employee_id.company_id.ecc and rec.date_from:
                if rec.holiday_status_id.annual_leave or rec.holiday_status_id.casual_leave:
                    if rec.employee_id.hire_date:
                        three_months = rec.employee_id.hire_date + relativedelta(months=3)
                        if rec.date_from.date() <= three_months:
                            raise ValidationError(
                                _("Annual & Causal Leave Can Be Requested After 3 Months From Hire Date "))
                    else:
                        raise ValidationError(_("Employee Must Have Hire Date"))

    # @api.constrains('holiday_status_id', 'employee_id')
    # def check_pilgrimage_leave(self):
    #     for rec in self:
    #         if rec.holiday_status_id.pilgrimage_leave:
    #             if not rec.employee_id.hire_date:
    #                 raise ValidationError(_("You Can Not Request Leave From This Type"))
    #             date_difference = relativedelta(date.today(), rec.employee_id.hire_date)
    #             if date_difference.years < 5:
    #                 raise ValidationError(_("You Can Not Request Leave From This Type"))

    # @api.constrains('remain_days_current_months', 'alloc_days_current_months', 'leaves_days_current_months', 'state')
    # def check_remain_notification(self):
    #     for rec in self:
    #         if rec.state not in ['refuse', 'cancel', 'draft']:
    #             if rec.alloc_days_current_months > 0:
    #                 if rec.remain_days_current_months < 0:
    #                     title = _("Remaining Days")
    #                     message = _(
    #                         "Remaining Days {} Of {}".format(round(rec.remain_days_current_months, 2),
    #                                                          round(rec.alloc_days_current_months, 2)))
    #                     self.env['bus.bus']._sendone(self.env.user.partner_id, 'web_notify', {
    #                         'title': title,
    #                         'message': message,
    #                         'sticky': True,
    #                         'type': 'danger',
    #                     })
    # elif rec.remain_days_current_months > 0:
    #     title = _("Remaining Days")
    #     message = _(
    #         "Remaining Days {} Of {}".format(round(rec.remain_days_current_months, 2),
    #                                          round(rec.alloc_days_current_months, 2)))
    #     rec.env['bus.bus']._sendone(rec.env.user.partner_id, 'web_notify', {
    #         'title': title,
    #         'message': message,
    #         'sticky': True,
    #         'type': 'info',
    #     })

    # @api.depends('date_from', 'date_to', 'holiday_status_id', 'employee_id', 'number_of_days', 'state')
    # def compute_remain_days_current_months(self):
    #     for rec in self:
    #         taken_leaves = 0
    #         taken_alloc = 0
    #         if rec.holiday_status_id and rec.holiday_status_id.requires_allocation == 'yes' and rec.employee_id and rec.state not in [
    #             'refuse', 'cancel', 'draft']:
    #             data_days = (rec.holiday_status_id.get_employees_days([rec.employee_id.id])[rec.employee_id.id])
    #
    #             result = data_days.get(rec.holiday_status_id.id, {})
    #             taken_alloc = result.get('taken_alloc', 0)
    #             taken_leaves = result.get('taken_leaves', 0)
    #
    #         rec.remain_days_current_months = taken_alloc - taken_leaves
    #         rec.alloc_days_current_months = taken_alloc
    #         rec.leaves_days_current_months = taken_leaves

    @api.constrains('date_from', 'holiday_status_id', 'date_to')
    def check_submit_after(self):
        for rec in self:
            if rec.date_to:
                request_date_to = rec.date_to.date()
                if rec.holiday_status_id.submit_after >= 0:
                    last_date = request_date_to
                    days = rec.holiday_status_id.submit_after
                    _weekdays = rec.employee_id.resource_calendar_id._get_weekdays()
                    print(_weekdays)
                    if not _weekdays:
                        raise ValidationError(_("Employee Has No Working Schedule"))
                    public_holidays = rec.env['hr.holidays.public.line'].search(
                        [('company_id', '=', rec.employee_id.company_id.id)]).mapped('date')
                    while days > 0:
                        last_date += timedelta(days=1)
                        if last_date.weekday() in _weekdays and last_date not in public_holidays:
                            days -= 1

                    if last_date < datetime.today().date():
                        raise ValidationError(
                            _("{} Can Be Submitted After The Request Date By {} Days ".format(
                                rec.holiday_status_id.name, rec.holiday_status_id.submit_after)))

    @api.constrains('date_from', 'holiday_status_id', 'date_to')
    def check_submit_before(self):
        for rec in self:
            if rec.date_to:
                request_date_from = rec.date_from.date()
                if rec.holiday_status_id.submit_before >= 0:
                    last_date = request_date_from
                    days = rec.holiday_status_id.submit_before
                    _weekdays = rec.employee_id.resource_calendar_id._get_weekdays()
                    print(_weekdays)
                    if not _weekdays:
                        raise ValidationError(_("Employee Has No Working Schedule"))
                    public_holidays = rec.env['hr.holidays.public.line'].search(
                        [('company_id', '=', rec.employee_id.company_id.id)]).mapped('date')
                    while days > 0:
                        last_date -= timedelta(days=1)
                        if last_date.weekday() in _weekdays and last_date not in public_holidays:
                            days -= 1

                    if last_date < datetime.today().date():
                        raise ValidationError(
                            _("{} Can Be Submitted Before The Request Date By {} Days".format(
                                rec.holiday_status_id.name, rec.holiday_status_id.submit_before)))

    @api.constrains('date_from', 'holiday_status_id', 'date_to', 'number_of_days', 'employee_id')
    def check_submit_5days_before(self):
        for rec in self:
            if rec.date_to:
                request_date_from = rec.date_from.date()
                if rec.holiday_status_id.submit_5days_before >= 0 and rec.number_of_days >= 5 and (
                        rec.employee_id.company_id.ecc or rec.employee_id.company_id.smart_pack):
                    last_date = request_date_from
                    days = rec.holiday_status_id.submit_5days_before
                    _weekdays = rec.employee_id.resource_calendar_id._get_weekdays()
                    print(_weekdays)
                    if not _weekdays:
                        raise ValidationError(_("Employee Has No Working Schedule"))
                    public_holidays = rec.env['hr.holidays.public.line'].search(
                        [('company_id', '=', rec.employee_id.company_id.id)]).mapped('date')
                    while days > 0:
                        last_date -= timedelta(days=1)
                        if last_date.weekday() in _weekdays and last_date not in public_holidays:
                            days -= 1

                    if last_date < datetime.today().date():
                        raise ValidationError(
                            _("{} (5 Days Or More) Can Be Submitted Before The Request Date By {} Days".format(
                                rec.holiday_status_id.name, rec.holiday_status_id.submit_5days_before)))

    def get_intervals_for_consecutive_days(self, date_from, date_to):
        intervals = []
        if date_to >= date_from:
            date_begin = date_from
            while date_begin <= date_to:
                date_end = min(date(date_begin.year, date_begin.month,
                                    calendar.monthrange(date_begin.year, date_begin.month)[1]), date_to)
                intervals.append((date_begin, date_end))
                date_begin = date_end + timedelta(days=1)
        return intervals

    def get_end_week(self, a_date):
        days_world = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5,
                      "Sunday": 6}
        days_egypt = {"Saturday": 0, "Sunday": 1, "Monday": 2, "Tuesday": 3, "Wednesday": 4, "Thursday": 5,
                      "Friday": 6}
        week_day = a_date.weekday() - 5 if a_date.weekday() > 5 else a_date.weekday() - 5 + 7
        delta = 6 - week_day
        return a_date + timedelta(days=delta)

    def get_start_week(self, a_date):
        days_world = {"Monday": 0, "Tuesday": 1, "Wednesday": 2, "Thursday": 3, "Friday": 4, "Saturday": 5,
                      "Sunday": 6}
        days_egypt = {"Saturday": 0, "Sunday": 1, "Monday": 2, "Tuesday": 3, "Wednesday": 4, "Thursday": 5,
                      "Friday": 6}
        week_day = a_date.weekday() - 5 if a_date.weekday() > 5 else a_date.weekday() - 5 + 7
        return a_date - timedelta(days=week_day)

    def get_intervals_for_work_home(self, date_from, date_to):
        intervals = []
        if date_to >= date_from:
            date_begin = date_from
            while date_begin <= date_to:
                week_end = self.get_end_week(date_begin)
                date_end = min(week_end, date_to)
                intervals.append((date_begin, date_end))
                date_begin = date_end + timedelta(days=1)
        return intervals

    # @api.constrains('date_from', 'date_to', 'holiday_status_id', 'employee_id', 'state')
    # def check_home_work(self):
    #     for rec in self:
    #         if rec.holiday_status_id.work_from_home and rec.employee_id and rec.state not in ['cancel', 'refuse']:
    #             if rec.date_from and rec.date_to and rec.date_to >= rec.date_from:
    #                 intervals = rec.get_intervals_for_work_home(rec.date_from.date(), rec.date_to.date())
    #                 for interval in intervals:
    #                     from_date = datetime.combine(interval[0], time(2, 0, 0))
    #                     to_date = datetime.combine(interval[1], time(21, 59, 59))
    #                     days = rec._get_number_of_days(from_date, to_date, rec.employee_id.id)['days']
    #                     if days > rec.employee_id.allowed_work_home:
    #                         raise ValidationError(
    #                             _("Maximum Days Per Week {}".format(rec.employee_id.allowed_work_home)))
    #                     if interval[1] < rec.get_end_week(interval[1]):
    #                         leave = rec.env['hr.leave'].search(
    #                             [('holiday_status_id', '=', rec.holiday_status_id.id),
    #                              ('employee_id', '=', rec.employee_id.id),
    #                              ('id', '!=', rec.id),
    #                              ('state', '!=', 'refuse'),
    #                              ('request_date_from', '>', interval[1])],
    #                             order="date_from", limit=1)
    #                         if leave:
    #                             if leave.number_of_days + days > rec.employee_id.allowed_work_home:
    #                                 raise ValidationError(
    #                                     _("Maximum Days Per Week {}".format(rec.employee_id.allowed_work_home)))
    #
    #                     if interval[0] > rec.get_start_week(interval[0]):
    #                         leave = rec.env['hr.leave'].search(
    #                             [('holiday_status_id', '=', rec.holiday_status_id.id),
    #                              ('employee_id', '=', rec.employee_id.id),
    #                              ('id', '!=', rec.id),
    #                              ('state', '!=', 'refuse'),
    #                              ('request_date_to', '<', interval[0])],
    #                             order="date_to asc", limit=1)
    #                         if leave:
    #                             if leave.number_of_days + days > rec.employee_id.allowed_work_home:
    #                                 raise ValidationError(
    #                                     _("Maximum Days Per Week {}".format(rec.employee_id.allowed_work_home)))

    # @api.constrains('date_from', 'date_to', 'holiday_status_id', 'employee_id', 'state')
    # def check_consecutive_days(self):
    #     for rec in self:
    #         if rec.holiday_status_id.consecutive_days_per_month >= 0 and rec.state not in ['cancel', 'refuse']:
    #             if rec.date_from and rec.date_to and rec.date_to >= rec.date_from:
    #                 intervals = rec.get_intervals_for_consecutive_days(rec.date_from.date(), rec.date_to.date())
    #                 for interval in intervals:
    #                     from_date = datetime.combine(interval[0], time(2, 0, 0))
    #                     to_date = datetime.combine(interval[1], time(21, 59, 59))
    #                     days = rec._get_number_of_days(from_date, to_date, rec.employee_id.id)['days']
    #                     if days > rec.holiday_status_id.consecutive_days_per_month:
    #                         raise ValidationError(
    #                             _("{} Maximum Number Consecutive Days Per Month {}".format(
    #                                 rec.holiday_status_id.name, rec.holiday_status_id.consecutive_days_per_month)))
    #                     if interval[1].day < calendar.monthrange(interval[1].year, interval[1].month)[1]:
    #                         leave = rec.env['hr.leave'].search(
    #                             [('holiday_status_id', '=', rec.holiday_status_id.id),
    #                              ('employee_id', '=', rec.employee_id.id),
    #                              ('id', '!=', rec.id),
    #                              ('state', '!=', 'refuse'),
    #                              ('request_date_from', '>', interval[1])],
    #                             order="date_from", limit=1)
    #                         if leave:
    #                             if leave.number_of_days + days > rec.holiday_status_id.consecutive_days_per_month:
    #                                 _weekdays = rec.employee_id.resource_calendar_id._get_weekdays()
    #                                 if _weekdays:
    #                                     weekdays = _weekdays
    #                                 else:
    #                                     raise ValidationError(_('No Valid Work Schedule Found.'))
    #
    #                                 date_from = interval[1] + timedelta(days=1)
    #                                 date_to = leave.request_date_from - timedelta(days=1)
    #                                 if date_to >= date_from:
    #                                     scheduled_workdays = rrule.rrule(rrule.DAILY, dtstart=date_from,
    #                                                                      wkst=rrule.SU,
    #                                                                      until=date_to,
    #                                                                      byweekday=weekdays)
    #                                     if scheduled_workdays:
    #                                         public_holidays = rec.env['hr.holidays.public.line'].search([]).mapped(
    #                                             'date')
    #                                         all_public_holiday = True
    #                                         for day in scheduled_workdays:
    #                                             if not public_holidays or day not in public_holidays:
    #                                                 all_public_holiday = False
    #
    #                                         if all_public_holiday:
    #                                             raise ValidationError(
    #                                                 _("{} Maximum Number Consecutive Days Per Month {} ".format(
    #                                                     rec.holiday_status_id.name,
    #                                                     rec.holiday_status_id.consecutive_days_per_month)))
    #                                     else:
    #                                         raise ValidationError(
    #                                             _("{} Maximum Number Consecutive Days Per Month {}".format(
    #                                                 rec.holiday_status_id.name,
    #                                                 rec.holiday_status_id.consecutive_days_per_month)))
    #                                 else:
    #                                     raise ValidationError(
    #                                         _("{} Maximum Number Consecutive Days Per Month {} ".format(
    #                                             rec.holiday_status_id.name,
    #                                             rec.holiday_status_id.consecutive_days_per_month)))
    #                     if interval[0].day > 1:
    #                         leave = rec.env['hr.leave'].search(
    #                             [('holiday_status_id', '=', rec.holiday_status_id.id),
    #                              ('employee_id', '=', rec.employee_id.id),
    #                              ('id', '!=', rec.id),
    #                              ('state', '!=', 'refuse'),
    #                              ('request_date_to', '<', interval[0])],
    #                             order="date_to asc", limit=1)
    #                         if leave:
    #                             if leave.number_of_days + days > rec.holiday_status_id.consecutive_days_per_month:
    #                                 _weekdays = rec.employee_id.resource_calendar_id._get_weekdays()
    #                                 if _weekdays:
    #                                     weekdays = _weekdays
    #                                 else:
    #                                     raise ValidationError(_('No Valid Work Schedule Found.'))
    #
    #                                 date_from = leave.request_date_to + timedelta(days=1)
    #                                 date_to = interval[0] - timedelta(days=1)
    #                                 if date_to >= date_from:
    #                                     scheduled_workdays = rrule.rrule(rrule.DAILY, dtstart=date_from,
    #                                                                      wkst=rrule.SU,
    #                                                                      until=date_to,
    #                                                                      byweekday=weekdays)
    #                                     if scheduled_workdays:
    #                                         public_holidays = rec.env['hr.holidays.public.line'].search([]).mapped(
    #                                             'date')
    #                                         all_public_holiday = True
    #                                         for day in scheduled_workdays:
    #                                             if not public_holidays or day not in public_holidays:
    #                                                 all_public_holiday = False
    #
    #                                         if all_public_holiday:
    #                                             raise ValidationError(
    #                                                 _("{} Maximum Number Consecutive Days Per Month {} ".format(
    #                                                     rec.holiday_status_id.name,
    #                                                     rec.holiday_status_id.consecutive_days_per_month)))
    #                                     else:
    #                                         raise ValidationError(
    #                                             _("{} Maximum Number Consecutive Days Per Month {} ".format(
    #                                                 rec.holiday_status_id.name,
    #                                                 rec.holiday_status_id.consecutive_days_per_month)))
    #                                 else:
    #                                     raise ValidationError(
    #                                         _("{} Maximum Number Consecutive Days Per Month {}".format(
    #                                             rec.holiday_status_id.name,
    #                                             rec.holiday_status_id.consecutive_days_per_month)))

    # def get_consecutive_types(self, type):
    #     leave = self.env['hr.leave'].search(
    #         [('holiday_status_id', '=', type.id),
    #          ('employee_id', '=', self.employee_id.id),
    #          ('id', '!=', self.id),
    #          ('state', '!=', 'refuse'),
    #          ('request_date_from', '>', self.request_date_to)],
    #         order="date_from", limit=1)
    #     if leave:
    #         _weekdays = self.employee_id.resource_calendar_id._get_weekdays()
    #         if _weekdays:
    #             weekdays = _weekdays
    #         else:
    #             raise ValidationError(_('No Valid Work Schedule Found.'))
    #
    #         date_from = self.request_date_to + timedelta(days=1)
    #         date_to = leave.request_date_from - timedelta(days=1)
    #         if date_to >= date_from:
    #             scheduled_workdays = rrule.rrule(rrule.DAILY, dtstart=date_from,
    #                                              wkst=rrule.SU,
    #                                              until=date_to,
    #                                              byweekday=weekdays)
    #             if scheduled_workdays:
    #                 public_holidays = self.env['hr.holidays.public.line'].search([]).mapped(
    #                     'date')
    #                 all_public_holiday = True
    #                 for day in scheduled_workdays:
    #                     if not public_holidays or day not in public_holidays:
    #                         all_public_holiday = False
    #
    #                 if all_public_holiday:
    #                     raise ValidationError(
    #                         _("{} & {} Consecutive Leave Types Is Not Allowed".format(
    #                             self.holiday_status_id.name,
    #                             leave.holiday_status_id.name)))
    #             else:
    #                 raise ValidationError(
    #                     _("{} & {} Consecutive Leave Types Is Not Allowed".format(
    #                         self.holiday_status_id.name,
    #                         leave.holiday_status_id.name)))
    #         else:
    #             raise ValidationError(
    #                 _("{} & {} Consecutive Leave Types Is Not Allowed".format(
    #                     self.holiday_status_id.name,
    #                     leave.holiday_status_id.name)))
    #
    #     leave = self.env['hr.leave'].search(
    #         [('holiday_status_id', '=', type.id),
    #          ('employee_id', '=', self.employee_id.id),
    #          ('id', '!=', self.id),
    #          ('state', '!=', 'refuse'),
    #          ('request_date_to', '<', self.request_date_from)],
    #         order="date_to desc", limit=1)
    #     if leave:
    #         _weekdays = self.employee_id.resource_calendar_id._get_weekdays()
    #         if _weekdays:
    #             weekdays = _weekdays
    #         else:
    #             raise ValidationError(_('No Valid Work Schedule Found.'))
    #
    #         date_from = leave.request_date_to + timedelta(days=1)
    #         date_to = self.request_date_from - timedelta(days=1)
    #         if date_to >= date_from:
    #             scheduled_workdays = rrule.rrule(rrule.DAILY, dtstart=date_from,
    #                                              wkst=rrule.SU,
    #                                              until=date_to,
    #                                              byweekday=weekdays)
    #             if scheduled_workdays:
    #                 public_holidays = self.env['hr.holidays.public.line'].search([]).mapped(
    #                     'date')
    #                 all_public_holiday = True
    #                 for day in scheduled_workdays:
    #                     if not public_holidays or day not in public_holidays:
    #                         all_public_holiday = False
    #
    #                 if all_public_holiday:
    #                     raise ValidationError(
    #                         _("{} & {} Consecutive Leave Types Is Not Allowed".format(
    #                             self.holiday_status_id.name,
    #                             leave.holiday_status_id.name)))
    #             else:
    #                 raise ValidationError(
    #                     _("{} & {} Consecutive Leave Types Is Not Allowed".format(
    #                         self.holiday_status_id.name,
    #                         leave.holiday_status_id.name)))
    #         else:
    #             raise ValidationError(
    #                 _("{} & {} Consecutive Leave Types Is Not Allowed".format(
    #                     self.holiday_status_id.name,
    #                     leave.holiday_status_id.name)))
    #
    # @api.constrains('date_from', 'date_to', 'holiday_status_id', 'employee_id')
    # def check_consecutive_types(self):
    #     for rec in self:
    #         if rec.holiday_status_id.not_allowed_consecutive_types and rec.state not in ['cancel', 'refuse']:
    #             if rec.date_from and rec.date_to and rec.date_to >= rec.date_from:
    #                 for type in rec.holiday_status_id.not_allowed_consecutive_types:
    #                     rec.get_consecutive_types(type)
    #         consecutive_types = rec.env['hr.leave.type'].search(
    #             [('not_allowed_consecutive_types', 'in', rec.holiday_status_id.ids)])
    #         for type in consecutive_types:
    #             rec.get_consecutive_types(type)

    def write(self, values):
        if 'state' in values and values['state'] != 'validate':
            validated_leaves = self.filtered(lambda l: l.state == 'validate')
            validated_leaves.sudo()._remove_resource_leave()

        employee_id = values.get('employee_id', False)
        if not self.env.context.get('leave_fast_create'):
            if values.get('state'):
                self._check_approval_update(values['state'])
                if any(holiday.validation_type == 'both' for holiday in self):
                    if values.get('employee_id'):
                        employees = self.env['hr.employee'].browse(values.get('employee_id'))
                    else:
                        employees = self.mapped('employee_id')
                    self.sudo()._check_double_validation_rules(employees, values['state'])
            if 'date_from' in values:
                values['request_date_from'] = values['date_from']
            if 'date_to' in values:
                values['request_date_to'] = values['date_to']
        result = super(models.Model, self).write(values)

        return result

    # @api.constrains('holiday_status_id', 'employee_id', 'date_from')
    # def check_probation_period(self):
    #     for rec in self:
    #         rec = rec.sudo()
    #         if rec.holiday_status_id.requires_allocation == 'yes':
    #             rec.before_trial_period = False
    #             contract_ids = rec.employee_id.contract_ids.sorted(key=lambda item: item.date_start, reverse=True)
    #             if contract_ids:
    #                 contract_id = contract_ids[0]
    #                 if contract_id and contract_id.trial_date_end:
    #                     if rec.date_from.date() <= contract_id.trial_date_end:
    #                         self.env['bus.bus']._sendone(self.env.user.partner_id, 'web_notify', {
    #                             'title': "Leaves",
    #                             'message': "You Request A Leave Before The End Of Trial Period",
    #                             'sticky': True,
    #                             'type': 'danger',
    #                         })
    #                         rec.before_trial_period = True
    #                         # raise ValidationError(_("You Can Not Request Leave Until The End Of Trial Period"))
