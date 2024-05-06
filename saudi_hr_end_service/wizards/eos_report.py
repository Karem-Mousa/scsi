from odoo import models, fields, api, _
from odoo.exceptions import ValidationError


class EosReport(models.TransientModel):
    _name = 'eos.report'

    employee_id = fields.Many2one('hr.employee', string='Employee')

    date = fields.Date(string='Date', required=True)

    def action_get_data(self):
        employee = self.env['hr.employee'].search([('id','=',self.employee_id.id)])
        domain = []
        if self.employee_id:
            domain.append(('id', '=', self.employee_id.id))

        if self.date:
            domain.append(('start_calculation_date', '<=', self.date))

        if employee:
            if employee.total_unpaid_loan > 0:
                raise ValidationError(_('Employee loans are not solved '))
            if employee.custody_count > 0:
                raise ValidationError(_('Employee custody are not solved '))


        return {
            'name': _('End of Service Report'),
            'type': 'ir.actions.act_window',
            'view_type': 'form',
            'domain' : domain,
            'view_mode': 'tree',
            'res_model': 'hr.employee',
            'target': 'current',
        }
