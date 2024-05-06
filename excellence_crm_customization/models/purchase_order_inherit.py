from odoo import models, fields, api, tools, _


class ExcPurchaseOrderInherit(models.Model):
    _inherit = "purchase.order"

    # x_ads_date = fields.Datetime(string="Ads Date")
    # x_opportunity_id = fields.Many2one('crm.lead')
    state = fields.Selection(selection_add=[('accounting_approve', 'Accounting Approve'), ('to approve',)])

    # def button_awarding_done(self):
    #     self.write({'state': 'awarding_done'})
    #     return {}

    def button_accounting_approve(self):
        self.write({'state': 'accounting_approve'})
        return {}

    def button_confirm(self):
        for order in self:
            if order.state not in ['draft', 'sent', 'accounting_approve']:
                continue
            order._add_supplier_to_product()
            # Deal with double validation process
            if order._approval_allowed():
                order.button_approve()
            else:
                order.write({'state': 'to approve'})
            if order.partner_id not in order.message_partner_ids:
                order.message_subscribe([order.partner_id.id])
        return True
