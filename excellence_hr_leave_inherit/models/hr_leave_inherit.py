from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class HrLeave(models.Model):
    _inherit = "hr.leave"

    @api.constrains('holiday_status_id')
    def _annual_leave(self):
        for emp in self.employee_ids:
            emp_annual_leaves = self.env['hr.leave'].sudo().search([('employee_id', '=', emp.id),
                                                                    ('holiday_status_id.is_annual_leave', '=', True),
                                                                    ('state', '=', 'validate')])
            emp_annual_leave_num = sum(emp_annual_leaves.mapped('number_of_days'))
            if self.holiday_status_id.is_emergency_leave and emp_annual_leave_num < 21:
                raise ValidationError("%s Cannot request emergency leave since it has annual leave" % emp.name)
