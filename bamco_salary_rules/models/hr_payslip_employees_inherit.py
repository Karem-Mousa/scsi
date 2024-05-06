# -*- coding: utf-8 -*-

from odoo import models, fields, api


class hr_payslip_employees_inherit(models.TransientModel):
    _inherit = 'hr.payslip.employees'

    def _get_employees(self):
        return []
        # active_employee_ids = self.env.context.get('active_employee_ids', False)
        # if active_employee_ids:
        #     return self.env['hr.employee'].browse(active_employee_ids)
        # # YTI check dates too
        # return self.env['hr.employee'].search(self._get_available_contracts_domain())

    employee_ids = fields.Many2many('hr.employee', 'hr_employee_group_rel', 'payslip_id', 'employee_id', 'Employeses',
                                    default=lambda self: self._get_employees(),
                                    required=True, readonly=False)

    @api.onchange('structure_id')
    def move_some_rules_to_current_structure(self):
        if self.structure_id:
            self = self.sudo()
            # get rules that is shared_between_structures=true
            shared_rules = self.env['hr.salary.rule'].search(
                [('shared_between_structures', '=', True), ('shared_structure', 'in', self.structure_id.ids)])
            print('aaaaaaaaaaaa', shared_rules)
            for sal_rule in shared_rules:
                sal_rule.struct_id = self.structure_id.id

# class hr_payslip_inherit(models.Model):
#     _inherit = 'hr.payslip'
#
#     @api.onchange('struct_id')
#     def move_some_rules_to_current_structure(self):
#         if self.struct_id:
#             self = self.sudo()
#             # get rules that is shared_between_structures=true
#             shared_rules = self.env['hr.salary.rule'].search(
#                 [('shared_between_structures', '=', True), ('shared_structure', 'in', self.struct_id.ids)])
#             print('aaaaaaaaaaaa', shared_rules)
#             for sal_rule in shared_rules:
#                 sal_rule.struct_id = self.struct_id.id
