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

    def get_days_cost(self, wage_per_day, total_days_before, total_days):
        result = 0
        if total_days > 0:
            if total_days_before <= 30:
                remain_before = 30 - total_days_before
                if total_days > remain_before:
                    total_days -= remain_before
                else:
                    total_days -= total_days
                if total_days > 30:
                    result += 30 * wage_per_day * 0.25
                    total_days -= 30
                else:
                    result += total_days * wage_per_day * 0.25
                    total_days -= total_days
                if total_days > 180:
                    result += 180 * wage_per_day * 0.75
                    total_days -= 180
                else:
                    result += total_days * wage_per_day * 0.75
                    total_days -= total_days
                if total_days > 0:
                    result += total_days * wage_per_day
            elif 60 >= total_days_before > 30:
                remain_before = 60 - total_days_before
                if total_days > remain_before:
                    result += remain_before * wage_per_day * 0.25
                    total_days -= remain_before
                else:
                    result += total_days * wage_per_day * 0.25
                    total_days -= total_days
                if total_days > 180:
                    result += 180 * wage_per_day * 0.75
                    total_days -= 180
                else:
                    result += total_days * wage_per_day * 0.75
                    total_days -= total_days
                if total_days > 0:
                    result += total_days * wage_per_day
            elif 240 >= total_days_before > 60:
                remain_before = 240 - total_days_before
                if total_days > remain_before:
                    result += remain_before * wage_per_day * 0.75
                    total_days -= remain_before
                else:
                    result += total_days * wage_per_day * 0.75
                    total_days -= total_days
                if total_days > 0:
                    result += total_days * wage_per_day
            elif total_days_before > 240:
                if total_days > 0:
                    result += total_days * wage_per_day
        return result

    def get_sick_leaves(self, payslip):
        employee_id = payslip.dict.employee_id
        contract_id = payslip.dict.contract_id
        wage_per_day = contract_id.wage / 30
        date_from = payslip.dict.date_from
        date_to = payslip.dict.date_to
        # date_from = datetime(date_from.year, date_from.month, date_from.day, 0, 0, 0) - timedelta(hours=2)
        # date_to = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59) - timedelta(hours=2)
        sick_leave = self.env['hr.leave.type'].search([('sick', '=', True)], limit=1)
        result = 0
        if sick_leave:
            total_days_before = employee_id.get_leave_days(date_to=date_from - timedelta(days=1), leave_type=sick_leave)
            total_days = employee_id.get_leave_days(date_from, date_to, sick_leave)
            result += employee_id.get_days_cost(wage_per_day, total_days_before, total_days)
            print(total_days_before)
            print(total_days)
            print(result)

        return -1 * result

    # def get_unpaid_leaves(self, payslip):
    #     employee_id = payslip.dict.employee_id
    #     contract_id = payslip.dict.contract_id
    #     date_from = payslip.dict.date_from
    #     date_to = payslip.dict.date_to
    #     date_from = datetime(date_from.year, date_from.month, date_from.day, 0, 0, 0)
    #     date_to = datetime(date_to.year, date_to.month, date_to.day, 23, 59, 59)
    #     unpaid_leave = self.env['hr.leave.type'].search([('unpaid', '=', True)], limit=1)
    #     total_days = 0
    #     if unpaid_leave:
    #         leaves = self.env['hr.leave'].search([('date_from', '>=', date_from),
    #                                               ('date_from', '<=', date_to),
    #                                               ('date_to', '>=', date_from),
    #                                               ('date_to', '<=', date_to),
    #                                               ('employee_id', '=', employee_id.id),
    #                                               ('state', '=', 'validate'),
    #                                               ('holiday_status_id', '=', unpaid_leave.id)
    #                                               ])
    #         total_days += sum(leaves.mapped('number_of_days'))
    #
    #         leaves = self.env['hr.leave'].search([('date_from', '>=', date_from),
    #                                               ('date_from', '<=', date_to),
    #                                               ('date_to', '>', date_to),
    #                                               ('employee_id', '=', employee_id.id),
    #                                               ('state', '=', 'validate'),
    #                                               ('holiday_status_id', '=', unpaid_leave.id)
    #                                               ])
    #         total_days += sum(
    #             [employee_id._get_work_days_data_batch_custom(item.date_from, date_to)[employee_id.id]['days'] for item in leaves])
    #
    #         leaves = self.env['hr.leave'].search([('date_to', '>=', date_from),
    #                                               ('date_to', '<=', date_to),
    #                                               ('date_from', '<', date_from),
    #                                               ('employee_id', '=', employee_id.id),
    #                                               ('state', '=', 'validate'),
    #                                               ('holiday_status_id', '=', unpaid_leave.id)
    #                                               ])
    #         total_days += sum(
    #             [employee_id._get_work_days_data_batch_custom(date_from, item.date_to)[employee_id.id]['days'] for item in leaves])
    #     wage_per_day = (contract_id.basic_salary * contract_id.basic_percentage / 100) / 30
    #     return -1 * total_days * wage_per_day
