from odoo import api, fields, models


class FinancialIdentificationRequest(models.Model):
    _name = 'financial.identification.request'
    _rec_name = 'employee_id'

    to = fields.Char(
        string='إلى',
        required=False)
    employee_id = fields.Many2one('hr.employee', 'الاسم', required=1)
    employee_number = fields.Char(string='رقم الموظف', related='employee_id.attendance_id_char', store=1)

    employment_date = fields.Date(string='تاريخ التعيين', related='employee_id.hiring_date', store=1)

    department_id = fields.Many2one('hr.department', string='الإدارة', related='employee_id.department_id', store=1)

    id_number = fields.Char(string='رقم الهوية', related='employee_id.identification_id', store=1)

    passport_number = fields.Char(string='رقم الجواز', related='employee_id.passport_id', store=1)

    nationality = fields.Many2one('res.country', 'الجنسية', related='employee_id.country_id', store=True)

    job_position = fields.Many2one('hr.job', string='الوظيفة', related='employee_id.job_id', store=1)

    basic_salary = fields.Monetary(string='الراتب الأساسى', related='employee_id.contract_id.wage', store=1)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)

    housing_allowance = fields.Float(string='بدل السكن', related='employee_id.contract_id.house_allowance', store=1)

    other_allowance = fields.Float(string='اخرى', related='employee_id.contract_id.other_allowance', store=1)

    total = fields.Float(
        string='اجمالى الراتب',
        required=False)

    bank = fields.Char(
        string='الحساب البنكى',
        required=False)
    bank_number = fields.Char(
        string='رقم الحساب',
        required=False)

    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.total = self.other_allowance + self.housing_allowance + self.basic_salary
            if self.employee_id.bank_name:
                self.bank = self.employee_id.bank_name.name + '/' + 'اسم البنك'
            if self.employee_id.bank_number:
                self.bank_number = self.employee_id.bank_number + '/' + 'الايبان'


class ManagerialIdentificationRequest(models.Model):
    _name = 'managerial.identification.request'
    _rec_name = 'employee_id'

    to = fields.Char(
        string='إلى',
        required=False)
    employee_id = fields.Many2one('hr.employee', 'الاسم', required=1)
    employee_number = fields.Char(string='رقم الموظف', related='employee_id.attendance_id_char', store=1)

    employment_date = fields.Date(string='تاريخ التعيين', related='employee_id.hiring_date', store=1)

    department_id = fields.Many2one('hr.department', string='الإدارة', related='employee_id.department_id', store=1)

    id_number = fields.Char(string='رقم الهوية', related='employee_id.identification_id', store=1)

    passport_number = fields.Char(string='رقم الجواز', related='employee_id.passport_id', store=1)

    nationality = fields.Many2one('res.country', 'الجنسية', related='employee_id.country_id', store=True)

    job_position = fields.Many2one('hr.job', string='الوظيفة', related='employee_id.job_id', store=1)

    basic_salary = fields.Monetary(string='الراتب الأساسى', related='employee_id.contract_id.wage', store=1)
    currency_id = fields.Many2one(string="Currency", related='company_id.currency_id', readonly=True)

    housing_allowance = fields.Float(string='بدل السكن', related='employee_id.contract_id.house_allowance', store=1)

    other_allowance = fields.Float(string='اخرى', related='employee_id.contract_id.other_allowance', store=1)

    total = fields.Float(
        string='اجمالى الراتب',
        required=False)

    bank = fields.Char(
        string='الحساب البنكى',
        required=False)
    bank_number = fields.Char(
        string='رقم الحساب',
        required=False)

    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.total = self.other_allowance + self.housing_allowance + self.basic_salary
            if self.employee_id.bank_name:
                self.bank = self.employee_id.bank_name.name + '/' + 'اسم البنك'
            if self.employee_id.bank_number:
                self.bank_number = self.employee_id.bank_number + '/' + 'الايبان'
