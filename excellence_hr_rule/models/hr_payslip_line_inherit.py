from odoo import fields, models, api, _


class HrPayslipLine(models.Model):
    _inherit = "hr.payslip.line"


    @api.model
    def create(self, vals):
        res = super(HrPayslipLine, self).create(vals)
        if res.salary_rule_id.x_show_partner:
            res.partner_id = res.slip_id.employee_id.address_home_id.id
        return res


