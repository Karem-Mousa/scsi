from odoo import models, fields, api, _
from datetime import date, datetime, time, timedelta
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError
from odoo import models, fields, api, _
from datetime import datetime, date
from collections import defaultdict
from datetime import timedelta
from pytz import utc

from odoo import api, fields, models
from odoo.tools import float_utils
from odoo.exceptions import ValidationError

# This will generate 16th of days
ROUNDING_FACTOR = 16
from collections import defaultdict
from dateutil.relativedelta import relativedelta
from pytz import utc

from odoo import api, fields, models


def timezone_datetime(time):
    if not time.tzinfo:
        time = time.replace(tzinfo=utc)
    return time


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    # current_smart_pack = fields.Boolean(compute="compute_current_company", store=True)
    #
    # @api.onchange('company_id')
    # @api.depends('company_id')
    # def compute_current_company(self):
    #     for rec in self:
    #         current_ecc = False
    #         current_factory = False
    #         current_smart_pack = False
    #         if rec.company_id.ecc:
    #             current_ecc = True
    #         elif rec.company_id.factory:
    #             current_factory = True
    #         elif rec.company_id.smart_pack:
    #             current_smart_pack = True
    #
    #         rec.current_smart_pack = current_smart_pack
    def _get_work_days_data_batch_custom(self, from_datetime, to_datetime, compute_leaves=False, calendar=None,
                                         domain=None):
        """
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.

            `domain` is used in order to recognise the leaves to take,
            None means default value ('time_type', '=', 'leave')

            Returns a dict {'days': n, 'hours': h} containing the
            quantity of working time expressed as days and as hours.
        """
        resources = self.mapped('resource_id')
        mapped_employees = {e.resource_id.id: e.id for e in self}
        result = {}

        # naive datetimes are made explicit in UTC
        from_datetime = timezone_datetime(from_datetime)
        to_datetime = timezone_datetime(to_datetime)

        mapped_resources = defaultdict(lambda: self.env['resource.resource'])
        for record in self:
            mapped_resources[calendar or record.resource_calendar_id] |= record.resource_id

        for calendar, calendar_resources in mapped_resources.items():
            if not calendar:
                for calendar_resource in calendar_resources:
                    result[calendar_resource.id] = {'days': 0, 'hours': 0}
                continue
            day_total = calendar._get_resources_day_total(from_datetime, to_datetime, calendar_resources)

            # actual hours per day
            if compute_leaves:
                intervals = calendar._work_intervals_batch(from_datetime, to_datetime, calendar_resources, domain)
            else:
                intervals = calendar._attendance_intervals_batch(from_datetime, to_datetime, calendar_resources)

            for calendar_resource in calendar_resources:
                result[calendar_resource.id] = calendar._get_days_data(intervals[calendar_resource.id],
                                                                       day_total[calendar_resource.id])

        # convert "resource: result" into "employee: result"
        return {mapped_employees[r.id]: result[r.id] for r in resources}

    def get_leave_days(self, date_from=date(1900, 1, 1), date_to=date.today(), leave_type=False):
        employee_id = self
        date_from_date = date_from
        date_to_date = date_to
        date_from = datetime(date_from.year, date_from.month, date_from.day, 0, 0, 0) - timedelta(hours=2)
        date_to = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59) - timedelta(hours=2)
        total_days = 0
        if leave_type:
            leaves = self.env['hr.leave'].search([('date_from', '>=', date_from),
                                                  ('date_from', '<=', date_to),
                                                  ('date_to', '>=', date_from),
                                                  ('date_to', '<=', date_to),
                                                  ('employee_id', '=', employee_id.id),
                                                  ('state', '=', 'validate'),
                                                  ('holiday_status_id', '=', leave_type.id)
                                                  ])
            sum_days = sum(leaves.mapped('number_of_days')) - sum(leaves.mapped('annual_days'))
            total_days += sum_days if sum_days > 0 else 0
            # total_days += sum([(item.request_date_to - item.request_date_from).days + 1 for item in leaves])

            leaves = self.env['hr.leave'].search([('date_from', '>=', date_from),
                                                  ('date_from', '<=', date_to),
                                                  ('date_to', '>', date_to),
                                                  ('employee_id', '=', employee_id.id),
                                                  ('state', '=', 'validate'),
                                                  ('holiday_status_id', '=', leave_type.id)
                                                  ])
            if not leave_type.consume_weekends:
                total_days += sum(
                    [employee_id._get_work_days_data_batch_custom(item.date_from, date_to)[employee_id.id]['days'] for
                     item
                     in leaves])
            else:
                total_days += sum([(date_to_date - item.request_date_from).days + 1 for item in leaves])

            leaves = self.env['hr.leave'].search([('date_to', '>=', date_from),
                                                  ('date_to', '<=', date_to),
                                                  ('date_from', '<', date_from),
                                                  ('employee_id', '=', employee_id.id),
                                                  ('state', '=', 'validate'),
                                                  ('holiday_status_id', '=', leave_type.id)
                                                  ])
            if not leave_type.consume_weekends:
                total_days += sum(
                    [employee_id._get_work_days_data_batch_custom(date_from, item.date_to)[employee_id.id]['days'] for
                     item
                     in leaves])
            else:
                total_days += sum([(item.request_date_to - date_from_date).days + 1 for item in leaves])

            leaves = self.env['hr.leave'].search([('date_to', '>', date_to),
                                                  ('date_from', '<', date_from),
                                                  ('employee_id', '=', employee_id.id),
                                                  ('state', '=', 'validate'),
                                                  ('holiday_status_id', '=', leave_type.id)
                                                  ])
            if not leave_type.consume_weekends:
                total_days += sum(
                    [employee_id._get_work_days_data_batch_custom(date_from, date_to)[employee_id.id]['days'] for
                     item
                     in leaves])
            else:
                total_days += sum([(date_to_date - date_from_date).days + 1 for item in leaves])
        return total_days

    days_off = fields.Boolean()


def timezone_datetime(time):
    if not time.tzinfo:
        time = time.replace(tzinfo=utc)
    return time


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def _get_work_days_data_batch_custom(self, from_datetime, to_datetime, compute_leaves=False, calendar=None,
                                         domain=None):
        """
            By default the resource calendar is used, but it can be
            changed using the `calendar` argument.

            `domain` is used in order to recognise the leaves to take,
            None means default value ('time_type', '=', 'leave')

            Returns a dict {'days': n, 'hours': h} containing the
            quantity of working time expressed as days and as hours.
        """
        resources = self.mapped('resource_id')
        mapped_employees = {e.resource_id.id: e.id for e in self}
        result = {}

        # naive datetimes are made explicit in UTC
        from_datetime = timezone_datetime(from_datetime)
        to_datetime = timezone_datetime(to_datetime)

        mapped_resources = defaultdict(lambda: self.env['resource.resource'])
        for record in self:
            mapped_resources[calendar or record.resource_calendar_id] |= record.resource_id

        for calendar, calendar_resources in mapped_resources.items():
            if not calendar:
                for calendar_resource in calendar_resources:
                    result[calendar_resource.id] = {'days': 0, 'hours': 0}
                continue
            day_total = calendar._get_resources_day_total(from_datetime, to_datetime, calendar_resources)

            # actual hours per day
            if compute_leaves:
                intervals = calendar._work_intervals_batch(from_datetime, to_datetime, calendar_resources, domain)
            else:
                intervals = calendar._attendance_intervals_batch(from_datetime, to_datetime, calendar_resources)

            for calendar_resource in calendar_resources:
                result[calendar_resource.id] = calendar._get_days_data(intervals[calendar_resource.id],
                                                                       day_total[calendar_resource.id])

        # convert "resource: result" into "employee: result"
        return {mapped_employees[r.id]: result[r.id] for r in resources}

    def get_leave_days(self, date_from=date(1900, 1, 1), date_to=date.today(), leave_type=False):
        employee_id = self
        date_from_date = date_from
        date_to_date = date_to
        date_from = datetime(date_from.year, date_from.month, date_from.day, 0, 0, 0) - timedelta(hours=2)
        date_to = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59) - timedelta(hours=2)
        total_days = 0
        if leave_type:
            leaves = self.env['hr.leave'].search([('date_from', '>=', date_from),
                                                  ('date_from', '<=', date_to),
                                                  ('date_to', '>=', date_from),
                                                  ('date_to', '<=', date_to),
                                                  ('employee_id', '=', employee_id.id),
                                                  ('state', '=', 'validate'),
                                                  ('holiday_status_id', '=', leave_type.id)
                                                  ])
            sum_days = sum(leaves.mapped('number_of_days')) - sum(leaves.mapped('annual_days'))
            total_days += sum_days if sum_days > 0 else 0
            # total_days += sum([(item.request_date_to - item.request_date_from).days + 1 for item in leaves])

            leaves = self.env['hr.leave'].search([('date_from', '>=', date_from),
                                                  ('date_from', '<=', date_to),
                                                  ('date_to', '>', date_to),
                                                  ('employee_id', '=', employee_id.id),
                                                  ('state', '=', 'validate'),
                                                  ('holiday_status_id', '=', leave_type.id)
                                                  ])
            if not leave_type.consume_weekends:
                total_days += sum(
                    [employee_id._get_work_days_data_batch_custom(item.date_from, date_to)[employee_id.id]['days'] for
                     item
                     in leaves])
            else:
                total_days += sum([(date_to_date - item.request_date_from).days + 1 for item in leaves])

            leaves = self.env['hr.leave'].search([('date_to', '>=', date_from),
                                                  ('date_to', '<=', date_to),
                                                  ('date_from', '<', date_from),
                                                  ('employee_id', '=', employee_id.id),
                                                  ('state', '=', 'validate'),
                                                  ('holiday_status_id', '=', leave_type.id)
                                                  ])
            if not leave_type.consume_weekends:
                total_days += sum(
                    [employee_id._get_work_days_data_batch_custom(date_from, item.date_to)[employee_id.id]['days'] for
                     item
                     in leaves])
            else:
                total_days += sum([(item.request_date_to - date_from_date).days + 1 for item in leaves])

            leaves = self.env['hr.leave'].search([('date_to', '>', date_to),
                                                  ('date_from', '<', date_from),
                                                  ('employee_id', '=', employee_id.id),
                                                  ('state', '=', 'validate'),
                                                  ('holiday_status_id', '=', leave_type.id)
                                                  ])
            if not leave_type.consume_weekends:
                total_days += sum(
                    [employee_id._get_work_days_data_batch_custom(date_from, date_to)[employee_id.id]['days'] for
                     item
                     in leaves])
            else:
                total_days += sum([(date_to_date - date_from_date).days + 1 for item in leaves])
        return total_days

    days_off = fields.Boolean()

    def data_approve(self):
        for rec in self:
            super(HrEmployee, rec).data_approve()
            rec.create_allocations_hire_date()

    old_insurance_years = fields.Integer('Experience Years For Vacation Balance')

    def exceeded_50_year_date(self, dates):
        for m in self:
            if m.birthday or m.insurance_start_date:
                if m.birthday and m.insurance_start_date:
                    a_month1 = relativedelta(years=50)
                    remain = 10 - m.old_insurance_years
                    if remain > 0:
                        a_month2 = relativedelta(years=remain)
                    else:
                        a_month2 = relativedelta(years=0)
                    diff1 = dates - a_month1
                    diff2 = dates - a_month2
                    if diff1 > m.birthday or diff2 > m.insurance_start_date:
                        return True
                    else:
                        return False

                elif m.birthday:
                    a_month1 = relativedelta(years=50)
                    diff1 = dates - a_month1
                    if diff1 > m.birthday:
                        return True
                    else:
                        return False


                elif m.insurance_start_date:
                    remain = 10 - m.old_insurance_years
                    if remain > 0:
                        a_month1 = relativedelta(years=remain)
                    else:
                        a_month1 = relativedelta(years=0)
                    diff2 = dates - a_month1
                    if diff2 > m.insurance_start_date:
                        return True
                    else:
                        return False

    def get_date_of_exceeded(self):
        for m in self:
            if m.birthday or m.insurance_start_date:
                if m.birthday and m.insurance_start_date:
                    a_month1 = relativedelta(years=50)
                    remain = 10 - m.old_insurance_years
                    if remain > 0:
                        a_month2 = relativedelta(years=remain)
                    else:
                        a_month2 = relativedelta(years=0)
                    diff1 = m.birthday + a_month1
                    diff2 = m.insurance_start_date + a_month2
                    return min(diff1, diff2)

                elif m.birthday:
                    a_month1 = relativedelta(years=50)
                    diff1 = m.birthday + a_month1
                    return diff1


                elif m.insurance_start_date:
                    remain = 10 - m.old_insurance_years
                    if remain > 0:
                        a_month1 = relativedelta(years=remain)
                    else:
                        a_month1 = relativedelta(years=0)
                    diff2 = m.insurance_start_date + a_month1
                    return diff2

    def exceeded_50_year(self):
        for m in self:
            if m.old_insurance_years and m.old_insurance_years >= 10:
                return True
            if m.birthday or m.insurance_start_date:
                if m.birthday and m.insurance_start_date:
                    a_month1 = relativedelta(years=50)
                    remain = 10 - m.old_insurance_years
                    if remain > 0:
                        a_month2 = relativedelta(years=remain)
                    else:
                        a_month2 = relativedelta(years=0)
                    diff1 = fields.Date.today() - a_month1
                    diff2 = fields.Date.today() - a_month2
                    if diff1 > m.birthday or diff2 > m.insurance_start_date:
                        return True
                    else:
                        return False

                elif m.birthday:
                    a_month1 = relativedelta(years=50)
                    diff1 = fields.Date.today() - a_month1
                    if diff1 > m.birthday:
                        return True
                    else:
                        return False


                elif m.insurance_start_date:
                    remain = 10 - m.old_insurance_years
                    if remain > 0:
                        a_month1 = relativedelta(years=remain)
                    else:
                        a_month1 = relativedelta(years=0)
                    diff2 = fields.Date.today() - a_month1
                    if diff2 > m.insurance_start_date:
                        return True
                    else:
                        return False

    def transfer_allocations(self):
        today = date.today()
        transfers = self.env['transfer.allocation'].search(
            [('date_from', '<=', today), ('date_to', '>=', today), ('done', '=', False)])
        employees = self.env['hr.employee'].search([('hire_date', '!=', False)])
        for m in employees:
            if m.hire_date < today:
                for transfer in transfers:
                    if m.company_id.id == transfer.company_id.id:
                        transfer.done = True
                        total = 0
                        for leave_type in transfer.transfer_from:
                            data_days = leave_type.get_employees_days([m.id], transfer.date_from - timedelta(days=1))[
                                m.id]
                            result = data_days.get(leave_type.id, {})
                            remaining_leaves = result.get('remaining_leaves', 0)
                            total += remaining_leaves

                        if total > transfer.days:
                            total = transfer.days
                        if total > 0:
                            allocation = self.env['hr.leave.allocation'].create({
                                'name': transfer.transfer_to.name + ' Remaining Balance',
                                'holiday_status_id': transfer.transfer_to.id,
                                'holiday_type': 'employee',
                                'employee_id': m.id,
                                'date_from': date(datetime.now().year, 1, 1),
                                'date_to': transfer.date_to,
                                'number_of_days': total,
                                'is_remaining': True,
                            })
                            allocation.action_confirm()
                            allocation.action_validate()

    def create_allocations(self):
        leaves = self.env['hr.leave.type'].search(
            [('auto_allocation', '=', True), ('allocation_year', '=', str(date.today().year))])
        employees = self.env['hr.employee'].search([])
        for leave in leaves:
            if leave.depend_on_age:
                for m in employees:
                    if m.company_id.id == leave.company_id.id:
                        diff = fields.Date.today()
                        if m.hire_date and m.hire_date < diff:
                            if m.exceeded_50_year():
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': leave.name,
                                    'holiday_status_id': leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'date_from': date(datetime.now().year, 1, 1),
                                    'date_to': date(datetime.now().year, 12, 31),
                                    'number_of_days': leave.number_of_days_more_than_50_year,
                                })
                                allocation.action_confirm()
                                allocation.action_validate()
                            elif not m.exceeded_50_year():
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': leave.name,
                                    'holiday_status_id': leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'checked': True,
                                    'date_from': date(datetime.now().year, 1, 1),
                                    'date_to': date(datetime.now().year, 12, 31),
                                    'number_of_days': leave.number_of_days_less_than_50_year,
                                })
                                allocation.action_confirm()
                                allocation.action_validate()
            else:
                for m in employees:
                    if m.company_id.id == leave.company_id.id:
                        diff = fields.Date.today()
                        if m.hire_date and m.hire_date < diff:
                            if True:
                                print('ggggggg')
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': leave.name,
                                    'holiday_status_id': leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'date_from': date(datetime.now().year, 1, 1),
                                    'date_to': date(datetime.now().year, 12, 31),
                                    'number_of_days': leave.number_of_days,
                                })
                                allocation.action_confirm()
                                allocation.action_validate()

    def create_allocations_hire_date(self):
        leaves = self.env['hr.leave.type'].search(
            [('auto_allocation', '=', True), ('allocation_year', '=', str(date.today().year))])
        employees = [self]
        for leave in leaves:
            if leave.depend_on_age:
                for m in employees:
                    if m.company_id.id == leave.company_id.id:
                        if m.hire_date:
                            diff = fields.Date.today()
                            # if diff.year == m.hire_date.year:
                            if m.exceeded_50_year():
                                start_date = max(m.hire_date, date(date.today().year, 1, 1))
                                sum1 = leave.number_of_days_more_than_50_year
                                day_per_month = sum1 / 12
                                date_difference = relativedelta(date(date.today().year, 12, 31), start_date)
                                months = date_difference.months + ((date_difference.days) / 30)
                                number_of_days = months * day_per_month
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': m.name,
                                    'holiday_status_id': leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'date_from': start_date,
                                    'date_to': date(datetime.now().year, 12, 31),
                                    'number_of_days': number_of_days,
                                })
                                allocation.action_confirm()
                                allocation.action_validate()
                            elif not m.exceeded_50_year():
                                start_date = max(m.hire_date, date(date.today().year, 1, 1))
                                sum1 = leave.number_of_days_less_than_50_year
                                day_per_month = sum1 / 12
                                date_difference = relativedelta(date(date.today().year, 12, 31), start_date)
                                months = date_difference.months + ((date_difference.days) / 30)
                                number_of_days = months * day_per_month
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': m.name,
                                    'holiday_status_id': leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'date_from': start_date,
                                    'date_to': date(datetime.now().year, 12, 31),
                                    'number_of_days': number_of_days,
                                    'checked': True,
                                })
                                allocation.action_confirm()
                                allocation.action_validate()
                        else:
                            raise ValidationError(_("Employee Has No Hire Date"))
            else:
                for m in employees:
                    if m.company_id.id == leave.company_id.id:
                        if m.hire_date:
                            three_months = relativedelta(months=3)
                            diff = fields.Date.today()
                            if diff.year == m.hire_date.year:
                                if True:
                                    start_date = max(m.hire_date, date(date.today().year, 1, 1))
                                    print('ggggggg')
                                    sum1 = leave.number_of_days
                                    day_per_month = sum1 / 12
                                    date_difference = relativedelta(date(date.today().year, 12, 31), start_date)
                                    months = date_difference.months + ((date_difference.days) / 30)
                                    number_of_days = months * day_per_month
                                    allocation = self.env['hr.leave.allocation'].create({
                                        'name': m.name,
                                        'holiday_status_id': leave.id,
                                        'holiday_type': 'employee',
                                        'employee_id': m.id,
                                        'date_from': start_date,
                                        'date_to': date(datetime.now().year, 12, 31),
                                        'number_of_days': number_of_days,
                                    })
                                    allocation.action_confirm()
                                    allocation.action_validate()
                        else:
                            raise ValidationError(_("Employee Has No Hire Date"))

    def create_allocations_manual(self):
        leaves = self.env['hr.leave.type'].search(
            [('auto_allocation', '=', True), ('allocation_year', '=', str(date.today().year))])
        employees = self
        for leave in leaves:
            if leave.depend_on_age:
                for m in employees:
                    if m.company_id.id == leave.company_id.id:
                        if m.hire_date:
                            found_allocation = self.env['hr.leave.allocation'].search(
                                [('holiday_status_id', '=', leave.id), ('employee_id', '=', m.id),
                                 ('state', 'not in', ['cancel', 'refuse'])])
                            if found_allocation and len(found_allocation) > 0:
                                raise ValidationError(
                                    _("Employee {} Has Already Allocation Of {}".format(m.name, leave.name)))
                            if m.exceeded_50_year():
                                start_date = max(m.hire_date, date(date.today().year, 1, 1))
                                sum1 = leave.number_of_days_more_than_50_year
                                day_per_month = sum1 / 12
                                date_difference = relativedelta(date(date.today().year, 12, 31), start_date)
                                months = date_difference.months + ((date_difference.days) / 30)
                                number_of_days = months * day_per_month
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': leave.name,
                                    'holiday_status_id': leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'date_from': start_date,
                                    'date_to': date(datetime.now().year, 12, 31),
                                    'number_of_days': number_of_days,
                                })
                                allocation.action_confirm()
                                allocation.action_validate()
                            elif not m.exceeded_50_year():
                                start_date = max(m.hire_date, date(date.today().year, 1, 1))
                                sum1 = leave.number_of_days_less_than_50_year
                                day_per_month = sum1 / 12
                                date_difference = relativedelta(date(date.today().year, 12, 31), start_date)
                                months = date_difference.months + ((date_difference.days) / 30)
                                number_of_days = months * day_per_month
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': leave.name,
                                    'holiday_status_id': leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'checked': True,
                                    'date_from': start_date,
                                    'date_to': date(datetime.now().year, 12, 31),
                                    'number_of_days': number_of_days,
                                })
                                allocation.action_confirm()
                                allocation.action_validate()
                        else:
                            raise ValidationError(_("Employee Has No Hire Date"))
            else:
                for m in employees:
                    if m.company_id.id == leave.company_id.id:
                        if m.hire_date:
                            found_allocation = self.env['hr.leave.allocation'].search(
                                [('holiday_status_id', '=', leave.id), ('employee_id', '=', m.id),
                                 ('state', 'not in', ['cancel', 'refuse'])])
                            if found_allocation and len(found_allocation) > 0:
                                raise ValidationError(
                                    _("Employee {} Has Already Allocation Of {}".format(m.name, leave.name)))
                            if True:
                                start_date = max(m.hire_date, date(date.today().year, 1, 1))
                                sum1 = leave.number_of_days
                                day_per_month = sum1 / 12
                                date_difference = relativedelta(date(date.today().year, 12, 31), start_date)
                                months = date_difference.months + ((date_difference.days) / 30)
                                number_of_days = months * day_per_month
                                print('ggggggg')
                                allocation = self.env['hr.leave.allocation'].create({
                                    'name': leave.name,
                                    'holiday_status_id': leave.id,
                                    'holiday_type': 'employee',
                                    'employee_id': m.id,
                                    'date_from': start_date,
                                    'date_to': date(datetime.now().year, 12, 31),
                                    'number_of_days': number_of_days,
                                })
                                allocation.action_confirm()
                                allocation.action_validate()
                        else:
                            raise ValidationError(_("Employee Has No Hire Date"))

    def check_allocations(self):
        allocations = self.env['hr.leave.allocation'].search(
            [('holiday_status_id.depend_on_age', '=', True), ('holiday_status_id.auto_allocation', '=', True),
             ('checked', '=', True), ('holiday_status_id.allocation_year', '=', str(date.today().year))])
        for m in allocations:
            if m.date_from.year == datetime.now().year:
                if m.employee_id.exceeded_50_year():
                    sum = 0
                    for leave in m.holiday_status_id:
                        sum += leave.number_of_days_less_than_50_year
                    day_per_month = sum / 12
                    date_difference = relativedelta(date.today(),
                                                    date(m.date_from.year, m.date_from.month, m.date_from.day))
                    plus_days = 1
                    day_end_date = date.today().day
                    if day_end_date == 31:
                        plus_days += -1
                    elif day_end_date == 29:
                        plus_days += 1
                    elif day_end_date == 28:
                        plus_days += 2
                    months = date_difference.months + ((date_difference.days + plus_days) / 30)
                    number_of_days = months * day_per_month
                    m.action_refuse()
                    m.action_draft()
                    m.number_of_days = number_of_days
                    m.checked = False
                    m.action_confirm()
                    m.action_validate()
                    sum = 0
                    for leave in m.holiday_status_id:
                        sum += leave.number_of_days_more_than_50_year
                    day_per_month = sum / 12
                    date_difference = relativedelta(date(date.today().year, 12, 31), date.today())
                    months = date_difference.months + ((date_difference.days) / 30)
                    number_of_days = months * day_per_month
                    allocation = self.env['hr.leave.allocation'].create({
                        'name': m.name,
                        'holiday_status_id': m.holiday_status_id.id,
                        'holiday_type': 'employee',
                        'employee_id': m.employee_id.id,
                        'date_from': date.today(),
                        'date_to': date(date.today().year, 12, 31),
                        'number_of_days': number_of_days,
                    })
                    allocation.action_confirm()
                    allocation.action_validate()
