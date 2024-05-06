from odoo import models, fields, api, tools, _
from odoo.exceptions import UserError, ValidationError


class ExcTenderPurchaseOrdersInherit(models.Model):
    _inherit = "purchase.order"

    x_tenders_minutes_count = fields.Integer(compute='compute_tenders_minutes_count')
    x_project_duration = fields.Float()
    x_project_duration_uom = fields.Many2one('uom.uom', string='Duration Unit of Measure',
                                             domain="[('category_id.name', '=ilike', 'Working Time')]",
                                             default=lambda self: self._get_duration_default_value())

    def _get_duration_default_value(self):
        month_uom = self.env['uom.uom'].sudo().search([('name', '=ilike', 'Month')], limit=1)
        if month_uom:
            return month_uom.id
        else:
            return self.env['uom.uom'].sudo().search(['|', ('category_id.name', '=ilike', 'ساعات العمل'),
                                                      ('category_id.name', '=ilike', 'Working Time')], limit=1).id

    def action_new_tender_minute(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "excellences_tenders_minutes.purchase_action_tender_minute_new")
        action['context'] = {
            'default_po_id': self.id,
            'default_project_name': self.task_id.name
        }

        return action

    def get_tenders_minutes(self):
        self.ensure_one()
        return {
            'type': 'ir.actions.act_window',
            'name': 'Tender Minutes',
            'view_mode': 'tree,form',
            'res_model': 'excellence.tenders.minutes',
            'domain': [('po_id', '=', self.id)],
            'context': "{'create': False}"
        }

    def compute_tenders_minutes_count(self):
        for rec in self:
            tender_count = self.env['excellence.tenders.minutes'].search_count(
                [('po_id', '=', rec.id)])
            if tender_count:
                rec.x_tenders_minutes_count = tender_count
            else:
                rec.x_tenders_minutes_count = 0

    def write(self, values):
        if 'state' in values:
            if values['state'] == 'accounting_approve':
                if not self.x_tenders_minutes_count:
                    raise ValidationError(_("يجب إنشاء محضر العروض قبل التأكيد"))
        return super(ExcTenderPurchaseOrdersInherit, self).write(values)
