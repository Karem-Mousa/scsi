from odoo import models, fields, api, tools, _


class ExcHrExpenseInherit(models.Model):
    _inherit = "hr.expense"

    x_opportunity_id = fields.Many2one('crm.lead')
    x_ads_date = fields.Datetime()
    x_delivery_date = fields.Datetime()
    x_final_offer_preparation_date = fields.Datetime()






