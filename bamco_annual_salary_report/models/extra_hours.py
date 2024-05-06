from odoo import api, fields, models


class ExtraHoursType(models.Model):
    _inherit = 'hr.variable.allowance.deduction.type'

    is_extra_hours = fields.Boolean(string="Extra Hours", default=False)


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    period_month = fields.Integer(compute='compute_period_month', store=True)

    @api.depends('date_to')
    def compute_period_month(self):
        for rec in self:
            if rec.date_to:
                rec.period_month = rec.date_to.month


class HrVariableAllowanceDeduction(models.Model):
    _inherit = 'hr.variable.allowance.deduction'

    period_month = fields.Integer(compute='compute_period_month', store=True)

    @api.depends('date')
    def compute_period_month(self):
        for rec in self:
            if rec.date:
                rec.period_month = rec.date.month
