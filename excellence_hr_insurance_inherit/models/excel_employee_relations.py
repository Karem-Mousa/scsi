from odoo import fields, models, api


class ExcelEmployeeRelations(models.Model):
    _name = 'excel.employee.relations'
    _description = 'Description'

    employee_id = fields.Many2one('hr.employee')
    name = fields.Char(required=True)
    relation = fields.Selection([('child', 'Child'),
                                 ('wife', 'Wife'),
                                 ('parent', 'Parent')], required=True)
