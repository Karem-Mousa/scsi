from odoo import models, fields, api, _
import datetime
from dateutil.rrule import rrule, MONTHLY
from dateutil.relativedelta import relativedelta
from odoo.http import request
from datetime import datetime, date, time
from collections import defaultdict
import pytz
from odoo.addons.resource.models.resource import datetime_to_string, string_to_datetime, Intervals
import base64
from io import BytesIO

import xlsxwriter


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def action_annual_salary_statement(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Annual Salary Statement',
            'view_mode': 'form',
            'res_model': 'annual.salary.statement',
            'target': 'new',

        }


class AnnualSalaryStatement(models.TransientModel):
    _name = 'annual.salary.statement'
    _description = 'Annual Salary Statement'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    employee_ids = fields.Many2many(comodel_name="hr.employee", string="Employee")
    gentextfile = fields.Binary('Click On Save As Button To Download File', readonly=True)

    # @api.onchange('start_date', 'end_date')
    # def onchange_dates(self):
    #     months = []
    #     if self.start_date and self.end_date:
    #         start = self.start_date
    #         end = self.end_date
    #         dates = [dt for dt in rrule(MONTHLY, dtstart=start, until=end)]
    #         for i in dates:
    #             months.append(i.month)
    #         print('months', months)

    def get_basic_salary_rule(self, employee, month):
        basic_salary = self.env['hr.payslip'].search(
            [('employee_id', '=', employee.id), ('state', '=', 'done'), ('period_month', '=', month)])
        if basic_salary:
            lines_basic = basic_salary.line_ids.filtered(lambda l: l.code == 'BASIC')
            basic = lines_basic.total if lines_basic else 0
            total = basic
            return total
        else:
            return 0

    def get_house_allowance_rule(self, employee, month):
        house_allowance = self.env['hr.payslip'].search(
            [('employee_id', '=', employee.id), ('state', '=', 'done'), ('period_month', '=', month)])
        if house_allowance:
            lines_house_allowance = house_allowance.line_ids.filtered(lambda l: l.code == 'HASR')
            basic = lines_house_allowance.total if lines_house_allowance else 0
            total = basic
            return total
        else:
            return 0

    def get_transportation_allowance_rule(self, employee, month):
        tasr_allowance = self.env['hr.payslip'].search(
            [('employee_id', '=', employee.id), ('state', '=', 'done'), ('period_month', '=', month)])
        if tasr_allowance:
            lines_tasr_allowance = tasr_allowance.line_ids.filtered(lambda l: l.code == 'TASR')
            basic = lines_tasr_allowance.total if lines_tasr_allowance else 0
            total = basic
            return total
        else:
            return 0

    def other_allownces(self, employee, month):
        other_allowance = self.env['hr.payslip'].search(
            [('employee_id', '=', employee.id), ('state', '=', 'done'), ('period_month', '=', month)])
        if other_allowance:
            lines_other_allowance = other_allowance.line_ids.filtered(lambda l: l.code == 'OTHASR')
            basic = lines_other_allowance.total if lines_other_allowance else 0
            total = basic
            return total
        else:
            return 0

    def get_other_allownces(self, employee, month):
        other_allownces = self.env['hr.payslip'].search(
            [('employee_id', '=', employee.id), ('state', '=', 'done'), ('period_month', '=', month)])
        if other_allownces:
            lines_other_allownces = other_allownces.line_ids.filtered(lambda l: l.code == 'OTHASR')
            basic = lines_other_allownces.total if lines_other_allownces else 0
            total = basic
            return total
        else:
            return 0

    def other_deduction(self, employee, month):
        other_deduction = self.env['hr.payslip'].search(
            [('employee_id', '=', employee.id), ('state', '=', 'done'), ('period_month', '=', month)])
        if other_deduction:
            lines_other_deduction = other_deduction.line_ids.filtered(lambda l: l.code == 'OTHDASR')
            basic = lines_other_deduction.total if lines_other_deduction else 0
            total = basic
            return total
        else:
            return 0

    def loan(self, employee, month):
        loan = self.env['hr.payslip'].search(
            [('employee_id', '=', employee.id), ('state', '=', 'done'), ('period_month', '=', month)])
        if loan:
            lines_loan = loan.line_ids.filtered(lambda l: l.code == 'LOAN')
            basic = lines_loan.total if lines_loan else 0
            total = basic
            return total
        else:
            return 0

    def employee_insurance(self, employee, month):
        employee_insurance = self.env['hr.payslip'].search(
            [('employee_id', '=', employee.id), ('state', '=', 'done'), ('period_month', '=', month)])
        if employee_insurance:
            lines_employee_insurance = employee_insurance.line_ids.filtered(lambda l: l.code == 'EISR')
            basic = lines_employee_insurance.total if lines_employee_insurance else 0
            total = basic
            return total
        else:
            return 0

    def total_num_working_days_month(self, employee):
        contract_days = self.env['hr.contract'].search([('state', '=', 'open'), ('employee_id', '=', employee.id)])
        if contract_days:
            days = contract_days.num_working_days_month if contract_days.num_working_days_month else 0
            return days
        else:
            return 0

    def extra_amount(self, employee, month):
        variable = self.env['hr.variable.allowance.deduction'].search(
            [('employee_id', '=', employee.id), ('period_month', '=', month), ('type.is_extra_hours', '=', True)])
        total_amount = 0
        if variable:
            for v in variable:
                total_amount += v.amount
            return total_amount
        else:
            return 0

    def extra_hours(self, employee, month):
        variable = self.env['hr.variable.allowance.deduction'].search(
            [('employee_id', '=', employee.id), ('period_month', '=', month), ('type.is_extra_hours', '=', True)])
        total_add = 0
        if variable:
            for v in variable:
                total_add += v.add_amount
            return total_add
        else:
            return 0

    def generate_xlsx_report(self):

        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})

        table_header_formate = workbook.add_format({
            'bold': 1,
            'border': 1,
            'bg_color': '#AAB7B8',
            'font_size': '10',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })
        header_formate = workbook.add_format({
            'bold': 1,
            'border': 1,
            'bg_color': '#AAB7B8',
            'font_size': '17',
            'align': 'center',
            'valign': 'vcenter',
            'text_wrap': True
        })

        months = []
        if self.start_date and self.end_date:
            start = self.start_date
            end = self.end_date
            dates = [dt for dt in rrule(MONTHLY, dtstart=start, until=end)]
            for i in dates:
                months.append(i.month)
            print('months', months)

        for emp in self.employee_ids:
            row = 6
            col = 0
            sheet = workbook.add_worksheet(emp.name)
            sheet.right_to_left()
            sheet.merge_range(0, 2, 2, 4, 'الكشف السنوى للراتب', header_formate)
            sheet.write(2, 2, str(self.start_date), table_header_formate)
            sheet.write(2, 3, str(self.end_date), table_header_formate)
            sheet.write(5, 0, "رقم الموظف", table_header_formate)
            sheet.write(5, 1, "اسم الموظف", table_header_formate)
            sheet.write(5, 2, "الشهر", table_header_formate)
            sheet.write(5, 3, "ايام العمل", table_header_formate)
            sheet.write(5, 4, "ساعات الاضافى", table_header_formate)
            sheet.write(5, 5, "قيمة الاضافى", table_header_formate)
            sheet.write(5, 6, "الراتب الاساسى", table_header_formate)
            sheet.write(5, 7, "الراتب المستحق", table_header_formate)
            sheet.write(5, 8, "السكن المستحق", table_header_formate)
            sheet.write(5, 9, "الانتقال المستحق", table_header_formate)
            sheet.write(5, 10, "بدلات اخرى", table_header_formate)
            sheet.write(5, 11, "اجمالى الراتب", table_header_formate)
            sheet.write(5, 12, "خصومات اخرى", table_header_formate)
            sheet.write(5, 13, "خصم سلفه", table_header_formate)
            sheet.write(5, 14, "خصم تأمينات", table_header_formate)
            sheet.write(5, 15, "اجمالى الخصميات", table_header_formate)
            sheet.write(5, 16, "صافى الراتب", table_header_formate)

            for month in months:
                basic_salary = self.get_basic_salary_rule(emp, month)
                house_allowance = self.get_house_allowance_rule(emp, month)
                transportation = self.get_transportation_allowance_rule(emp, month)
                other_allownces = self.get_other_allownces(emp, month)
                total_allowance = basic_salary + house_allowance + transportation + other_allownces
                other_deduction = self.other_deduction(emp, month)
                loan = self.loan(emp, month)
                employee_insurance = self.employee_insurance(emp, month)
                total_deduction = other_deduction + loan + employee_insurance
                final_salary = total_allowance - total_deduction
                total_num_working_days_month = self.total_num_working_days_month(emp)
                extra_amount = self.extra_amount(emp, month)
                extra_hours = self.extra_hours(emp, month)
                sheet.write(row, col, emp.identification_id, table_header_formate)
                sheet.write(row, col + 1, emp.name, table_header_formate)
                sheet.write(row, col + 2, month, table_header_formate)
                sheet.write(row, col + 3, total_num_working_days_month, table_header_formate)
                sheet.write(row, col + 4, extra_hours, table_header_formate)
                sheet.write(row, col + 5, extra_amount, table_header_formate)
                sheet.write(row, col + 6, basic_salary, table_header_formate)
                sheet.write(row, col + 7, basic_salary, table_header_formate)
                sheet.write(row, col + 8, house_allowance, table_header_formate)
                sheet.write(row, col + 9, transportation, table_header_formate)
                sheet.write(row, col + 10, other_allownces, table_header_formate)
                sheet.write(row, col + 11, total_allowance, table_header_formate)
                sheet.write(row, col + 12, other_deduction, table_header_formate)
                sheet.write(row, col + 13, loan, table_header_formate)
                sheet.write(row, col + 14, employee_insurance, table_header_formate)
                sheet.write(row, col + 15, total_deduction, table_header_formate)
                sheet.write(row, col + 16, final_salary, table_header_formate)
            row += 1

        workbook.close()
        output.seek(0)

        self.write({'gentextfile': base64.encodestring(output.getvalue())})

        return {
            'type': 'ir.actions.act_url',
            'name': 'كشف السنوى للرواتب',
            'url': '/web/content/annual.salary.statement/%s/gentextfile/annual.xlsx?download=true' % (
                self.id),
            'target': 'new'
        }