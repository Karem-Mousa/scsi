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


class HrContractEmployees(models.Model):
    _name = 'hr.contract.employees'

    employee_ids = fields.Many2many('hr.employee', 'emp_contract_rel', 'emp_id', 'contr_id', 'Employees', required=True)
    gentextfile = fields.Binary('Click On Save As Button To Download File', readonly=True)

    def generate_contract_xlsx(self):
        output = BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet('معلومات الموظف')
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

        sheet.merge_range(0, 0, 0, 6, 'معلومات الموظف', table_header_formate)
        sheet.merge_range(0, 8, 0, 12, 'الراتب قبل', table_header_formate)
        sheet.merge_range(0, 14, 0, 18, 'الراتب بعد', table_header_formate)

        sheet.write(1, 0, 'الرقم الوظيفي', table_header_formate)
        sheet.write(1, 1, 'اسم الموظف', table_header_formate)
        sheet.write(1, 2, 'تاريخ التعيين', table_header_formate)
        sheet.write(1, 3, 'المهنة', table_header_formate)
        sheet.write(1, 4, 'القسم', table_header_formate)
        sheet.write(1, 5, 'الفرع', table_header_formate)
        sheet.write(1, 6, 'تاريخ الزيادة', table_header_formate)
        sheet.write(1, 8, 'أساسي', table_header_formate)
        sheet.write(1, 9, 'سكن', table_header_formate)
        sheet.write(1, 10, 'مواصلات', table_header_formate)
        sheet.write(1, 11, 'بدلات أخري', table_header_formate)
        sheet.write(1, 12, 'اجمالي', table_header_formate)
        sheet.write(1, 14, 'أساسي', table_header_formate)
        sheet.write(1, 15, 'سكن', table_header_formate)
        sheet.write(1, 16, 'مواصلات', table_header_formate)
        sheet.write(1, 17, 'بدلات أخري', table_header_formate)
        sheet.write(1, 18, 'اجمالي', table_header_formate)

        row = 2
        col = 0

        for rec in self.employee_ids:
            if rec.contract_id.state == 'open':
                total_before = rec.contract_id.basic_before + rec.contract_id.house_allowance_before + rec.contract_id.transportation_allowance_before + rec.contract_id.other_allowance_before
                total_after = rec.contract_id.wage + rec.contract_id.house_allowance + rec.contract_id.transportation_allowance + rec.contract_id.other_allowance
                sheet.write(row, col, rec.attendance_id_char or '', table_header_formate)
                sheet.write(row, col + 1, rec.arabic_name or '', table_header_formate)
                sheet.write(row, col + 2, rec.hiring_date.strftime("%Y-%m-%d") or '', table_header_formate)
                sheet.write(row, col + 3, rec.job_id.name or '', table_header_formate)
                sheet.write(row, col + 4, rec.area.name or '', table_header_formate)
                sheet.write(row, col + 5, rec.branch.name or '', table_header_formate)
                sheet.write(row, col + 5, rec.branch.name or '', table_header_formate)
                sheet.write(row, col + 6,
                            rec.contract_id.date_raise.strftime("%Y-%m-%d") if rec.contract_id.date_raise else ' ',
                            table_header_formate)
                sheet.write(row, col + 8, rec.contract_id.basic_before or 0, table_header_formate)
                sheet.write(row, col + 9, rec.contract_id.house_allowance_before or 0, table_header_formate)
                sheet.write(row, col + 10, rec.contract_id.transportation_allowance_before or 0, table_header_formate)
                sheet.write(row, col + 11, rec.contract_id.other_allowance_before or 0, table_header_formate)
                sheet.write(row, col + 12, total_before or 0, table_header_formate)

                sheet.write(row, col + 14, rec.contract_id.wage or 0, table_header_formate)
                sheet.write(row, col + 15, rec.contract_id.house_allowance or 0, table_header_formate)
                sheet.write(row, col + 16, rec.contract_id.transportation_allowance or 0, table_header_formate)
                sheet.write(row, col + 17, rec.contract_id.other_allowance or 0, table_header_formate)
                sheet.write(row, col + 18, total_after or 0, table_header_formate)
            row += 1

        workbook.close()
        output.seek(0)

        self.write({'gentextfile': base64.encodestring(output.getvalue())})
        return {
            'type': 'ir.actions.act_url',
            'name': 'معلومات الموظف',
            'url': '/web/content/hr.contract.employees/%s/gentextfile/معلومات الموظف.xlsx?download=true' % (
                self.id),
            'target': 'new'
        }
