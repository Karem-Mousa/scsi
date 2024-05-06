# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HREmployeeInh(models.Model):
    _inherit = 'hr.employee'

    attendance_id_char = fields.Char('الرقم الوظيفي')
    arabic_name = fields.Char('')
    contract_select = fields.Selection(
        [('saudi', 'Saudi'), ('non_saudi', 'Non Saudi'), ('special_expatriate', 'Special Expatriate'),
         ('other', 'Other')], string='نوع الموظف')

    insurance_end_date = fields.Date()
    social_insurance_no = fields.Char()
    social_insurance_office = fields.Char()
    insurance_position = fields.Char('Arabic Insurance Position')
    insurance_start_date = fields.Date()

    private_mobile_no = fields.Char('رقم الجوال الخاص')
    personal_email = fields.Char('الايميل الشخصي')
    constatnt_phone_no = fields.Char('هاتف ثابت')
    current_address = fields.Char('العنوان الحالي')
    state = fields.Selection(string="Employee State", selection=[
        ('فترة التجربة', 'فترة التجربة'),
        ('على راس العمل', 'على راس العمل'),
        ('مجاز', 'مجاز'),
        ('معلق', 'معلق'),
        ('منتهي  خدماته', 'منتهي  خدماته'),

    ], default='على راس العمل')
    area = fields.Many2one('hr.area', string='القسم')
    branch = fields.Many2one('hr.branch', string='الفرع')
    hiring_date = fields.Date(string='تاريخ الالتحاق')

    emp_status = fields.Selection(string="حالة الموظف", selection=[
        ('فترة التجربة', 'فترة التجربة'),
        ('على راس العمل', 'على راس العمل'),
        ('مجاز', 'مجاز'),
        ('معلق', 'معلق'),
        ('منتهي  خدماته', 'منتهي  خدماته')])

    @api.onchange('emp_status')
    def onchange_employee_state(self):
        for rec in self:
            if rec.emp_status:
                rec.state = rec.emp_status
