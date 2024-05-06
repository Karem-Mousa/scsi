# -*- coding: utf-8 -*-

from odoo import models, fields, api
from odoo.exceptions import ValidationError
from datetime import datetime, time, timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    def over_time_rate_salary(self, payslip, contract):
        payslip = payslip.dict
        overtime = self.env['over.time.configuration'].search([], limit=1, order='create_date desc').sudo().mapped(
            'overtime_rate')
        overtime_str = ' '.join(str(h) for h in overtime)
        overtime_rate = float(overtime_str) if overtime else 0
        overtime_request = self.env['over.time'].sudo().search([('employee_id', '=', payslip.employee_id.id)])
        if overtime_request:
            for over in overtime_request:
                over_date_from = over.date_from.date() + timedelta(days=1, hours=2)
                if payslip.date_from <= over_date_from <= payslip.date_to:
                    hour_rate = contract.num_working_days_month / contract.num_working_hours_day
                    employee_allow_rate = (contract.wage + contract.house_allowance) / hour_rate
                    total_hour_rate = employee_allow_rate * int(overtime_rate) * over.total_hours
                    total_employee_rate = (contract.wage / hour_rate) * overtime_rate * over.total_hours
                    overtime_total_rate = total_hour_rate + total_employee_rate
                    return overtime_total_rate
        else:
            return 0
