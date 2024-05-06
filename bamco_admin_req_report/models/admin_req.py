# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AdminRequest(models.Model):
    _name = 'admin.request'
    _description = 'Request'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string='إسم الموظف', required=1)
    employ_no = fields.Char('الرقم الوظيفي', related='employee_id.attendance_id_char', store=True)
    country_id = fields.Many2one('res.country', 'الجنسية', related='employee_id.country_id', store=True)
    job_id = fields.Many2one('hr.job', string='المسمى الوظيفي', related='employee_id.job_id', store=True)
    department_id = fields.Many2one('hr.department', string='القسم التابع له', related='employee_id.department_id',
                                    store=True)
    mobile_phone = fields.Char('رقم الجوال', related='employee_id.mobile_phone', store=True)
    direct_to = fields.Char('موجهة إلى', required=1)
    comment = fields.Text(
        string='بيان',
        required=False)
