# -*- coding: utf-8 -*-

from odoo import models, fields, api

class HrContractInherit(models.Model):
    _inherit = 'hr.contract'


    social_insurance_type = fields.Selection([
        ('amount', 'Amount'),
        ('percentage', 'Percentage'),
    ], string='Social Insurance Type', default='amount')
    social_insurance_percentage = fields.Float(string='Social Insurance (Monthly)')
    social_insurance = fields.Float(string='Social Insurance Amount (Monthly)')

    @api.onchange('social_insurance_percentage')
    def social_insurance_percentage_onchange(self):
        if self.social_insurance_type and self.social_insurance_type == 'percentage':
            self.social_insurance = (self.social_insurance_percentage * self.wage) / 100

    @api.onchange('social_insurance_type')
    def social_insurance_type_onchange(self):
        if self.social_insurance_percentage:
            self.social_insurance_percentage = 0.0



    medical_insurance_type = fields.Selection([
        ('amount', 'Amount'),
        ('percentage', 'Percentage'),
    ], string='Medical Insurance Type', default='amount')
    medical_insurance_percentage = fields.Float(string='Medical Insurance (Monthly)')
    medical_insurance = fields.Float(string='Medical Insurance Amount (Monthly)')

    @api.onchange('medical_insurance_percentage')
    def medical_insurance_percentage_onchange(self):
        if self.medical_insurance_type and self.medical_insurance_type == 'percentage':
            self.medical_insurance = (self.medical_insurance_percentage * self.wage) / 100

    @api.onchange('medical_insurance_type')
    def medical_insurance_type_onchange(self):
        if self.medical_insurance_percentage:
            self.medical_insurance_percentage = 0.0

    transportation_allowance_type = fields.Selection([
        ('amount', 'Amount'),
        ('percentage', 'Percentage'),
    ], string='Transportation Type', default='amount')
    transportation = fields.Float(string='Transportation (Monthly)')
    transportation_amount = fields.Float(string='Transportation Amount (Monthly)')

    @api.onchange('transportation')
    def transportation_onchange(self):
        if self.transportation_allowance_type and self.transportation_allowance_type == 'percentage':
            self.transportation_amount = (self.transportation * self.wage) / 100

    @api.onchange('transportation_allowance_type')
    def transportation_allowance_type_onchange(self):
        if self.transportation:
            self.transportation = 0.0

    with_accommodation = fields.Boolean(string='With Accommodation')
    house_periodic = fields.Boolean(string='Periodic')
    house_allowance_type = fields.Selection([
        ('amount', 'Amount'),
        ('percentage', 'Percentage'),
    ], string='House Type', default='amount')
    house_number_of_months = fields.Integer(string='NO.Of Months', default=1)
    housing = fields.Float(string='Housing (Monthly)')
    housing_amount = fields.Float(string='Housing Amount')
    house_date = fields.Date(string='Housing Date')

    @api.onchange('housing')
    def housing_onchange(self):
        if self.house_allowance_type and self.house_allowance_type == 'percentage':
            if self.house_periodic:
                self.housing_amount = (self.housing * self.wage * self.house_number_of_months) / 100
            else:
                self.housing_amount = (self.housing * self.wage) / 100

    @api.onchange('house_allowance_type')
    def house_allowance_type_onchange(self):
        if self.housing:
            self.housing = 0.0

    @api.onchange('with_accommodation')
    def with_accommodation_onchange(self):
        if self.with_accommodation:
            self.housing_amount = 0.0

    @api.onchange('house_number_of_months')
    def house_number_of_months_onchange(self):
        self.housing_amount = self.house_number_of_months * self.housing_amount

    natural_allowance_type = fields.Selection([
        ('amount', 'Amount'),
        ('percentage', 'Percentage'),
    ], string='Natural Work Type', default='amount')
    natural_work = fields.Float(string='Natural Work (Monthly)')
    natural_work_amount = fields.Float(string='Natural Work Amount (Monthly)')

    @api.onchange('natural_work')
    def natural_work_onchange(self):
        if self.natural_allowance_type and self.natural_allowance_type == 'percentage':
            self.natural_work_amount = (self.natural_work * self.wage) / 100

    @api.onchange('natural_allowance_type')
    def natural_allowance_type_onchange(self):
        if self.natural_work:
            self.natural_work = 0.0

    food_allowance_type = fields.Selection([
        ('amount', 'Amount'),
        ('percentage', 'Percentage'),
    ], string='Food Type', default='amount')
    food_allowance = fields.Float(string='Food (Monthly)')
    food_allowance_amount = fields.Float(string='Food Amount (Monthly)')

    @api.onchange('food_allowance')
    def food_allowance_onchange(self):
        if self.food_allowance_type and self.food_allowance_type == 'percentage':
            self.food_allowance_amount = (self.food_allowance * self.wage) / 100

    @api.onchange('food_allowance_type')
    def food_allowance_type_onchange(self):
        if self.food_allowance:
            self.food_allowance = 0.0

    mobile_allowance_type = fields.Selection([
        ('amount', 'Amount'),
        ('percentage', 'Percentage'),
    ], string='Mobile Type', default='amount')
    mobile_allowance = fields.Float(string='Mobile (Monthly)')
    mobile_allowance_amount = fields.Float(string='Mobile Amount (Monthly)')

    @api.onchange('mobile_allowance')
    def mobile_allowance_onchange(self):
        if self.mobile_allowance_type and self.mobile_allowance_type == 'percentage':
            self.mobile_allowance_amount = (self.mobile_allowance * self.wage) / 100

    @api.onchange('mobile_allowance_type')
    def mobile_allowance_type_onchange(self):
        if self.mobile_allowance:
            self.mobile_allowance = 0.0

    car_allowance_type = fields.Selection([
        ('amount', 'Amount'),
        ('percentage', 'Percentage'),
    ], string='Car Type', default='amount')
    car_allowance = fields.Float(string='Car (Monthly)')
    car_allowance_amount = fields.Float(string='Car Amount (Monthly)')

    @api.onchange('car_allowance')
    def car_allowance_onchange(self):
        if self.car_allowance_type and self.car_allowance_type == 'percentage':
            self.car_allowance_amount = (self.car_allowance * self.wage) / 100

    @api.onchange('car_allowance_type')
    def car_allowance_type_onchange(self):
        if self.car_allowance:
            self.car_allowance = 0.0





