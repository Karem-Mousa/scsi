from odoo import fields, models, api, _
from odoo.osv import expression


import pytz
from dateutil.relativedelta import relativedelta


class HrPayslipEmployees(models.TransientModel):
    _inherit = "hr.payslip.employees"

    @api.depends('structure_id')
    def _compute_employee_ids(self):
        for wizard in self:
            domain = wizard._get_available_contracts_domain()
            if wizard.structure_id:
                domain = expression.AND([
                    domain,
                    [('contract_id.structure_type_id.struct_ids', 'in', [self.structure_id.id])]
                ])
            wizard.employee_ids = self.env['hr.employee'].search(domain)
