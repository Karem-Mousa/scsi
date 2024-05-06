from odoo.exceptions import ValidationError

from dateutil import relativedelta

from odoo import models, fields, api, _
from odoo.http import request
from datetime import datetime, date, time
from collections import defaultdict
import pytz
from odoo.addons.resource.models.resource import datetime_to_string, string_to_datetime, Intervals
import base64
from io import BytesIO

import xlsxwriter


class HrPayslipEmployees(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _check_undefined_slots(self, work_entries, payslip_run):
        """
        Check if a time slot in the contract's calendar is not covered by a work entry
        """
        work_entries_by_contract = defaultdict(lambda: self.env['hr.work.entry'])
        for work_entry in work_entries:
            work_entries_by_contract[work_entry.contract_id] |= work_entry

        for contract, work_entries in work_entries_by_contract.items():
            calendar_start = pytz.utc.localize(
                datetime.combine(max(contract.date_start, payslip_run.date_start), time.min))
            calendar_end = pytz.utc.localize(
                datetime.combine(min(contract.date_end or date.max, payslip_run.date_end), time.max))
            outside = contract.resource_calendar_id._attendance_intervals_batch(calendar_start, calendar_end)[
                          False] - work_entries._to_intervals()
            # if outside:
            #     time_intervals_str = "\n - ".join(['', *["%s -> %s" % (s[0], s[1]) for s in outside._items]])
            #     raise UserError(_("Some part of %s's calendar is not covered by any work entry. Please complete the schedule. Time intervals to look for:%s") % (contract.employee_id.name, time_intervals_str))


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    gentextfile = fields.Binary('Click On Save As Button To Download File', readonly=True)

    def get_basic_salary_rule(self, employee):
        basic_salary = self.env['hr.payslip'].search(
            [('employee_id', '=', employee.id), ('id', 'in', self.slip_ids.ids)])
        if basic_salary:
            lines_basic = basic_salary.line_ids.filtered(lambda l: l.code == 'BASIC')
            basic = lines_basic.total if lines_basic else 0
            total = basic
            return total
        else:
            return 0

    def get_net_salary_rule(self, employee):
        net_salary = self.env['hr.payslip'].search([('employee_id', '=', employee.id), ('id', 'in', self.slip_ids.ids)])
        if net_salary:
            lines_net = net_salary.line_ids.filtered(lambda l: l.code == 'NET')
            net = lines_net.total if lines_net else 0
            total = net
            return total
        else:
            return 0

    def get_house_salary_rule(self, employee):
        house_salary = self.env['hr.payslip'].search(
            [('employee_id', '=', employee.id), ('id', 'in', self.slip_ids.ids)])
        if house_salary:
            lines_house = house_salary.line_ids.filtered(lambda l: l.code == 'HASR')
            house = lines_house.total if lines_house else 0
            total = house
            return total
        else:
            return 0

    def get_transportation_others_salary_rule(self, employee):
        transportation_other_salary = self.env['hr.payslip'].search(
            [('employee_id', '=', employee.id), ('id', 'in', self.slip_ids.ids)])
        if transportation_other_salary:
            lines_transportation = transportation_other_salary.line_ids.filtered(lambda l: l.code == 'TASR')
            lines_other = transportation_other_salary.line_ids.filtered(lambda l: l.code == 'OTHASR')
            transportation = lines_transportation.total if lines_transportation else 0
            other = lines_other.total if lines_other else 0
            total = transportation + other
            return total
        else:
            return 0

    def get_deductions_salary_rules(self, employee):
        deductions_salary = self.env['hr.payslip'].search(
            [('employee_id', '=', employee.id), ('id', 'in', self.slip_ids.ids)])
        if deductions_salary:
            lines_loan = deductions_salary.line_ids.filtered(lambda l: l.code == 'LOAN')
            lines_others = deductions_salary.line_ids.filtered(lambda l: l.code == 'OTHDASR')
            # lines_company = deductions_salary.line_ids.filtered(lambda l: l.code == 'CISR')
            lines_employee = deductions_salary.line_ids.filtered(lambda l: l.code == 'EISR')
            loan = lines_loan.total if lines_loan else 0
            others = lines_others.total if lines_others else 0
            # company = lines_company.total if lines_company else 0
            empl = lines_employee.total if lines_employee else 0
            total = loan + others + empl
            return total
        else:
            return 0

    def generate_bank_xlsx_report(self):
        if self.slip_ids:
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output, {'in_memory': True})
            sheet = workbook.add_worksheet('نموزج أجور')

            without_borders = workbook.add_format({
                'bold': 1,
                'border': 1,
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True,
                'font_size': '11',

            })

            table_header_formate = workbook.add_format({
                'bold': 1,
                'border': 1,
                'bg_color': '#AAB7B8',
                'font_size': '10',
                'align': 'center',
                'valign': 'vcenter',
                'text_wrap': True
            })
            font_size_10 = workbook.add_format(
                {'font_name': 'KacstBook', 'font_size': 10, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                 'border': 1})
            font_size_13 = workbook.add_format(
                {'font_name': 'KacstBook', 'font_size': 13, 'align': 'center', 'valign': 'vcenter', 'text_wrap': True,
                 'border': 1})

            sheet.right_to_left()
            sheet.write(0, 0, 'البنك', table_header_formate)
            sheet.write(0, 1, 'الآيبان', table_header_formate)
            sheet.write(0, 2, 'الاسم', table_header_formate)
            sheet.write(0, 3, 'الرقم الوظيفي', table_header_formate)
            sheet.write(0, 4, 'الهوية', table_header_formate)
            sheet.write(0, 5, 'الصافي', table_header_formate)
            sheet.write(0, 6, 'الأساسي', table_header_formate)
            sheet.write(0, 7, 'السكن', table_header_formate)
            sheet.write(0, 8, 'إيرادات أخرى', table_header_formate)
            sheet.write(0, 9, 'الخصومات', table_header_formate)

            row = 1
            col = 0

            for rec in self.slip_ids:
                basic_salary = self.get_basic_salary_rule(rec.employee_id)
                net_salary = self.get_net_salary_rule(rec.employee_id)
                house_salary = self.get_house_salary_rule(rec.employee_id)
                transportation_others_salary = self.get_transportation_others_salary_rule(rec.employee_id)
                deductions_salary = self.get_deductions_salary_rules(rec.employee_id)
                sheet.write(row, col, rec.employee_id.bank_name.name or '', table_header_formate)
                sheet.write(row, col + 1, rec.employee_id.bank_number or '', table_header_formate)
                sheet.write(row, col + 2, rec.employee_id.arabic_name or '', table_header_formate)
                sheet.write(row, col + 3, rec.employee_id.attendance_id_char or '', table_header_formate)
                sheet.write(row, col + 4, rec.employee_id.identification_id or '', table_header_formate)
                sheet.write(row, col + 5, net_salary or 0, table_header_formate)
                sheet.write(row, col + 6, basic_salary or 0, table_header_formate)
                sheet.write(row, col + 7, house_salary or 0, table_header_formate)
                sheet.write(row, col + 8, transportation_others_salary or 0, table_header_formate)
                sheet.write(row, col + 9, deductions_salary or 0, table_header_formate)
                row += 1

            workbook.close()
            output.seek(0)

            self.write({'gentextfile': base64.encodestring(output.getvalue())})
            return {
                'type': 'ir.actions.act_url',
                'name': 'نموزج أجور',
                'url': '/web/content/hr.payslip.run/%s/gentextfile/نموزج أجور.xlsx?download=true' % (
                    self.id),
                'target': 'new'
            }
