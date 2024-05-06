from odoo import api, fields, models, _


class HRResignationRequest(models.Model):
    _name = 'hr.resignation.req'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', 'الاسم', required=1)
    employee_number = fields.Char(string='رقم الموظف', related='employee_id.attendance_id_char', store=1)
    job_position = fields.Many2one('hr.job', string='الوظيفة', related='employee_id.job_id', store=1)
    phone = fields.Char(string='رقم الجوال', related='employee_id.mobile_phone', store=1)
    employment_date = fields.Date(string='تاريخ التعيين', related='employee_id.hiring_date', store=1)
    department_id = fields.Many2one('hr.department', string='الإدارة', related='employee_id.department_id', store=1)
    id_number = fields.Char(string='رقم الهوية', related='employee_id.identification_id', store=1)
    passport_number = fields.Char(string='رقم الجواز', related='employee_id.passport_id', store=1)
    address_id = fields.Many2one('res.partner', string='موقع العمل', related='employee_id.address_id', store=1)
    area = fields.Many2one('hr.area', related='employee_id.area', store=1)
    last_work_day = fields.Date(
        string='اخر يوم عمل',
        required=False)

    reason = fields.Text(
        string="سبب الاستقالة",
        required=False)

    notes = fields.Text(
        string="ملاحظات المدير",
        required=False)

    # manager_notes = fields.Text(
    #     string="ملاحظات المدير",
    #     required=False)

    hr_comment = fields.Text(
        string="ملاحظات شئون الموظفين",
        required=False)
