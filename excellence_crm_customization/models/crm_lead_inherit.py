from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError


class ExcLeadInherit(models.Model):
    _inherit = "crm.lead"

    x_sheet_name = fields.Char(string="Sheet Name")
    x_sheet_price = fields.Float(string="Sheet Price")
    x_ads_date = fields.Datetime(string="Ads Date")
    x_delivery_date = fields.Datetime(string="Delivery Date")
    x_final_offer_preparation_date = fields.Datetime(string="Final Preparation Date")

    x_technical_offer_uploaded = fields.Boolean(string="Technical Offer Uploaded")
    x_financial_offer_uploaded = fields.Boolean(string="Financial Offer Uploaded")

    x_offer_delivered = fields.Boolean(string="Offer delivered")
    x_copy_offer_uploaded = fields.Boolean(string="copy_offer_uploaded")
    x_offer_delivered_date = fields.Datetime(string="Offer Delivered Date")
    x_offer_document = fields.Binary(string='Offer Attachment')

    x_awarding_document_uploaded = fields.Boolean(string='Awarding Document Uploaded')
    x_awarding_document = fields.Binary(string='Awarding Document')

    x_expenses_count = fields.Integer(compute='compute_expenses_count')

    def action_new_expense(self):
        action = self.env["ir.actions.actions"]._for_xml_id("excellence_crm_customization.new_hr_expense_action")

        action['context'] = {
            'default_x_opportunity_id': self.id,
            'default_x_final_offer_preparation_date': self.x_final_offer_preparation_date,
            'default_x_delivery_date': self.x_delivery_date,
            'default_x_ads_date': self.x_ads_date,
            'default_name': self.x_sheet_name,
            'default_total_amount': self.x_sheet_price
        }
        return action

    def get_expense(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Expenses',
            'view_mode': 'tree,form',
            'res_model': 'hr.expense',
            'domain': [('x_opportunity_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_expenses_count(self):
        for rec in self:
            rec.x_expenses_count = self.env['hr.expense'].search_count(
                [('x_opportunity_id', '=', rec.id)])

    def write(self, values):
        if 'stage_id' in values:
            # if values['stage_id'] not in [1, 2]:
            #     if not (
            #             self.x_sheet_name and self.x_sheet_price and self.x_ads_date and self.x_delivery_date and self.x_final_offer_preparation_date and self.x_expenses_count):
            #         raise ValidationError(_("يجب ملأ بيانات الكراسة وشرائها أولا"))

            if values['stage_id'] not in [1, 2, 3]:
                if not (self.partner_id and self.quotation_count and self.x_technical_offer_uploaded and
                        self.x_financial_offer_uploaded):
                    raise ValidationError(
                        _("You Should \n select customer \n check upload technical and financial offer"
                          " \n make a quotation  "))

            if values['stage_id'] not in [1, 2, 3, 5]:
                if not (self.x_offer_delivered and self.x_copy_offer_uploaded and self.x_offer_delivered_date and
                        self.x_offer_document):
                    raise ValidationError(
                        _("You Should Fill Required Offer Info Tab Fields "))

            if values['stage_id'] not in [1, 2, 3, 5, 6]:
                if not (self.x_awarding_document_uploaded and self.x_awarding_document):
                    raise ValidationError(
                        _("You Should Fill Awarding Offer Info Tab Fields "))

        return super(ExcLeadInherit, self).write(values)

    def action_new_quotation(self):
        action = super(ExcLeadInherit, self).action_new_quotation()
        action['context'] = {
            'default_x_project_name': self.name}
        return action


