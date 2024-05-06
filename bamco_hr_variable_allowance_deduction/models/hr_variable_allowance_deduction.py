from odoo import models, fields, api, _


class HrVariableAllowanceDeduction(models.Model):
    _name = 'hr.variable.allowance.deduction'

    employee_id = fields.Many2one('hr.employee')
    contract_id = fields.Many2one('hr.contract', compute='_get_contract_id', store=True)
    date = fields.Date()
    amount = fields.Float(readonly=True)
    add_amount = fields.Float('Add Amount')
    type = fields.Many2one('hr.variable.allowance.deduction.type')
    payslip_id = fields.Many2one('hr.payslip')

    @api.depends('employee_id')
    def _get_contract_id(self):
        running_contracts = self.env['hr.contract'].search([('employee_id', '=', self.employee_id.id),
                                                            ('state', '=', 'open')])
        if running_contracts:
            self.contract_id = running_contracts[0].id

    @api.onchange('type', 'add_amount')
    def _set_amount(self):
        if self.type and self.contract_id:
            if self.type.calculation_method == 'fixed':
                self.amount = self.add_amount * self.type.fixed_amount
            elif self.type.calculation_method == 'percentage':
                if self.type.basic_housing:
                    self.amount = (self.contract_id.basic_housing * self.type.percentage_amount * self.add_amount) / 100
                if self.type.basic_transport:
                    self.amount = (self.contract_id.basic_transport * self.type.percentage_amount * self.add_amount) / 100
                if self.type.gross:
                    self.amount = (self.contract_id.gross * self.type.percentage_amount * self.add_amount) / 100
                if not self.type.basic_housing and not self.type.gross and not self.type.basic_transport:
                    self.amount = (self.contract_id.wage * self.type.percentage_amount * self.add_amount) / 100
            elif self.type.calculation_method == 'work_day':
                if self.type.basic_housing:
                    self.amount = (self.contract_id.basic_housing / self.contract_id.num_working_days_month) * self.add_amount
                if self.type.basic_transport:
                    self.amount = (self.contract_id.basic_transport / self.contract_id.num_working_days_month) * self.add_amount
                if self.type.gross:
                    self.amount = (self.contract_id.gross / self.contract_id.num_working_days_month) * self.add_amount
                if not self.type.basic_housing and not self.type.gross and not self.type.basic_transport:
                    self.amount = (self.contract_id.wage / self.contract_id.num_working_days_month) * self.add_amount
            elif self.type.calculation_method == 'work_hour':
                result = 0
                is_condition = self.type.gross is True or self.type.half_wage is True or self.type.basic_housing is True or self.type.basic_transport is True

                if self.type.gross is True:
                    gross_amount = (self.contract_id.gross / (self.contract_id.num_working_days_month * self.contract_id.num_working_hours_day)) * self.add_amount
                    result += gross_amount
                if self.type.half_wage is True:
                    wage_amount = (self.contract_id.wage / (self.contract_id.num_working_days_month * self.contract_id.num_working_hours_day)) / 2 * self.add_amount
                    result += wage_amount
                if self.type.basic_housing is True:
                    basic_housing_amount = (self.contract_id.basic_housing / (self.contract_id.num_working_days_month * self.contract_id.num_working_hours_day)) * self.add_amount
                    result += basic_housing_amount
                if self.type.basic_transport is True:
                    basic_transport_amount = (self.contract_id.basic_transport / (self.contract_id.num_working_days_month * self.contract_id.num_working_hours_day)) * self.add_amount
                    result += basic_transport_amount
                if not is_condition:
                    result = (self.contract_id.wage / (self.contract_id.num_working_days_month * self.contract_id.num_working_hours_day)) * self.add_amount
                self.amount = result
                # if self.type.gross == False and self.type.half_wage == False and self.type.basic_housing == False:
                #     self.amount = (self.contract_id.wage /  (self.contract_id.num_working_days_month * self.contract_id.num_working_hours_day)) * self.add_amount
                # elif self.type.gross == True and self.type.half_wage == False and self.type.basic_housing == False:
                #     self.amount = (self.contract_id.gross / (self.contract_id.num_working_days_month * self.contract_id.num_working_hours_day)) * self.add_amount
                # elif self.type.gross == True and self.type.half_wage == True and self.type.basic_housing == True:
                #     gross_amount = (self.contract_id.gross / (self.contract_id.num_working_days_month * self.contract_id.num_working_hours_day)) * self.add_amount
                #     wage_amount = (self.contract_id.wage / (self.contract_id.num_working_days_month * self.contract_id.num_working_hours_day)) / 2 * self.add_amount
                #     basic_housing_amount = (self.contract_id.basic_housing / (self.contract_id.num_working_days_month * self.contract_id.num_working_hours_day)) / 2 * self.add_amount
                #     self.amount = gross_amount + wage_amount + basic_housing_amount
                # elif self.type.gross == False and self.type.half_wage == True and self.type.basic_housing == False:
                #     self.amount = (self.contract_id.wage / (self.contract_id.num_working_days_month * self.contract_id.num_working_hours_day)) / 2 * self.add_amount
                # elif self.type.gross == False and self.type.half_wage == False and self.type.basic_housing == True:
                #     self.amount = (self.contract_id.basic_housing / (self.contract_id.num_working_days_month * self.contract_id.num_working_hours_day)) * self.add_amount

            if self.type.type == 'deduction':
                self.amount *= 1
