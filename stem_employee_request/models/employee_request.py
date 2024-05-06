from email.policy import default

from odoo import fields, models, api, _


class EmployeeRequest(models.Model):
    _name = 'employee.request'
    _description = 'Employee request'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', required=True)
    directed_to_id = fields.Many2one(comodel_name="hr.employee", string="Directed To", required=False, )
    department = fields.Many2one('hr.department', related='employee_id.department_id', string="Department")
    req_type = fields.Char(string="Request Type", required=True)
    note = fields.Text('Note')
    state = fields.Selection([
        ('draft', 'Draft'),
        ('requested', 'Requested'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected')], string='State', default='draft')
