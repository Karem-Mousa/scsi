# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date

class HrEmployeeInherit(models.Model):
    _inherit = 'hr.employee'


    def compute_get_wage(self):
        for rec in self:
            total_wage = []
            contract = rec.contract_id
            # total_wage.append(contract.medical_insurance * -1 if contract.medical_insurance_type == 'percentage' else contract.medical_insurance_percentage * -1)
            # total_wage.append(contract.social_insurance * -1 if contract.social_insurance_type == 'percentage' else contract.social_insurance_percentage * -1)
            total_wage.append(contract.car_allowance_amount if contract.car_allowance_type == 'percentage' else contract.car_allowance)
            total_wage.append(contract.mobile_allowance_amount if contract.mobile_allowance_type == 'percentage' else contract.mobile_allowance)
            total_wage.append(contract.food_allowance_amount if contract.food_allowance_type == 'percentage' else contract.food_allowance)
            total_wage.append(contract.natural_work_amount if contract.natural_allowance_type == 'percentage' else contract.natural_work)
            total_wage.append(contract.transportation_amount if contract.transportation_allowance_type == 'percentage' else contract.transportation)
            total_wage.append(contract.housing_amount if contract.house_allowance_type == 'percentage' else contract.housing)
            total_wage.append(contract.house_allowance)
            total_wage.append(contract.transportation_allowance)
            total_wage.append(contract.wage)
            rec.total_contracts_wage_with_allowances = sum(total_wage)

    @api.depends('first_hiring_date', 'start_calculation_date')
    def compute_start_date(self):
        for rec in self:
            if rec.start_calculation_date:
                start_date = rec.start_calculation_date
                today = date.today()
                delta = today - start_date
                rec.no_of_days = delta.days
                rec.no_of_years = delta.days / 365
                if rec.opening_balance != 0.0:
                    rec.update({
                        'total_contracts_wage_with_allowances': 0.0,
                        'daily_total_eos': rec.opening_balance,
                        'total_eos_and_leaves': rec.opening_balance
                    })
                else:
                    if rec.no_of_years <= 5:
                        rec.daily_total_eos = (0.5 * rec.total_contracts_wage_with_allowances * rec.no_of_years)
                    else:
                        rec.daily_total_eos = (5 * (0.5 * rec.total_contracts_wage_with_allowances)) + ((rec.no_of_years - 5) * rec.total_contracts_wage_with_allowances)
                    rec.total_eos_and_leaves = rec.daily_total_eos + rec.total_leaves if rec.opening_balance == 0.0 else rec.opening_balance

    @api.depends('contract_id')
    def get_first_contract_date(self):
        for rec in self:
            contract = self.env['hr.contract'].search([('employee_id', '=', rec.id)],
                                                      order='date_start asc', limit=1)
            if contract:
                rec.first_hiring_date = contract.date_start
            else:
                rec.first_hiring_date = date.today()





    start_calculation_date = fields.Date(related='first_hiring_date')
    opening_balance = fields.Float(string="Opening Balance")
    no_of_years = fields.Float(compute='compute_start_date', digits=(16, 3))
    no_of_days = fields.Float(compute='compute_start_date')
    no_of_leaves = fields.Float(string="No. of Remaining Leaves")
    total_contracts_wage_with_allowances = fields.Float(string="Total Contracts Wage", compute='compute_get_wage')
    total_leaves = fields.Float(string="Total Leaves Amount")
    daily_total_eos = fields.Float(compute='compute_start_date')
    total_eos_and_leaves = fields.Float(compute='compute_start_date')

    first_hiring_date = fields.Date(string='Register Date', required=False, compute='get_first_contract_date')












