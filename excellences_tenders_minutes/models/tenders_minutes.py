from odoo import fields, models, api, _
from odoo.exceptions import ValidationError


class ExcTendersMinutes(models.Model):
    _name = 'excellence.tenders.minutes'
    _description = 'Description'

    name = fields.Char(required=True,
                       default=lambda self: _('New'))
    project_name = fields.Char()
    tender_created_date = fields.Date()
    responsible_employee = fields.Many2many('hr.employee')
    tender_minute_lines_ids = fields.One2many('excellence.tenders.minutes.line', 'tender_minute_id')
    selected_company = fields.Many2one('res.partner', readonly=True)
    selected_company_tender_amount = fields.Float(readonly=True, compute='change_selected_company_amount')
    user_id = fields.Many2one('res.users')
    signature_date = fields.Date()
    signature = fields.Html()
    po_id = fields.Many2one('purchase.order')
    tender_users_signature_ids = fields.One2many('excellence.tenders.minutes.signature', 'tender_minute_id')

    def action_add_signature(self):
        action = self.env["ir.actions.actions"]._for_xml_id(
            "excellences_tenders_minutes.action_tender_minute_add_signature")
        action['context'] = {
            'default_tender_minute_id': self.id
        }

        return action

    @api.model
    def create(self, vals):
        if vals.get('name', _("New")) == _("New"):
            vals['name'] = self.env['ir.sequence'].next_by_code(
                'excellence.tenders.minutes') or _("New")
            return super(ExcTendersMinutes, self).create(vals)

    @api.depends('tender_minute_lines_ids.tender_amount')
    def change_selected_company_amount(self):
        for rec in self:
            awarded_company = rec.tender_minute_lines_ids.filtered(lambda x: x.awarded)
            if awarded_company:
                rec.selected_company_tender_amount = awarded_company[0].tender_amount
            else:
                rec.selected_company_tender_amount = 0


class ExcTendersMinutesLines(models.Model):
    _name = 'excellence.tenders.minutes.line'
    _description = 'Description'

    tender_minute_id = fields.Many2one('excellence.tenders.minutes', required=True, ondelete='cascade')
    vendor_id = fields.Many2one('res.partner', required=True)
    tender_amount = fields.Float()
    paper_completed = fields.Boolean()
    technical_evaluation = fields.Float()
    technical_attachment = fields.Binary()
    technical_attachment_store_fname = fields.Char()
    financial_evaluation = fields.Float()
    financial_attachment = fields.Binary()
    financial_attachmen_store_fname = fields.Char()
    company_strength = fields.Float()
    awarded = fields.Boolean()

    @api.constrains('awarded')
    def check_checked_company(self):
        for rec in self:
            if rec.awarded:
                other_companies_awarded = self.sudo().search([('tender_minute_id', '=', rec.tender_minute_id.id),
                                                              ('id', '!=', rec._origin.id),
                                                              ('awarded', '=', True)])
                for company in other_companies_awarded:
                    company.awarded = False

                rec.tender_minute_id.selected_company = rec.vendor_id
                # rec.tender_minute_id.selected_company_tender_amount = rec.tender_amount


class ExcTendersMinutesSignatures(models.Model):
    _name = 'excellence.tenders.minutes.signature'
    _description = 'Description'

    tender_minute_id = fields.Many2one('excellence.tenders.minutes', required=True, ondelete='cascade')
    user_id = fields.Many2one('res.users', default=lambda self: self.env.user, readonly=True)
    user_job_position = fields.Char(related='user_id.partner_id.function')
    signature_date = fields.Date()
    signature = fields.Binary()

    # signature = fields.Html(default=lambda self: self.env.user.signature)

    @api.constrains('user_id')
    def check_unique_signature(self):
        for rec in self:
            user_signature = self.sudo().search([('tender_minute_id', '=', rec.tender_minute_id.id),
                                                 ('user_id', '=', rec.user_id.id),
                                                 ('id', '!=', rec.id)])
            if user_signature:
                raise ValidationError(_("تم إضافة توقيعك من قبل ، يمكنك التعديل عليه"))
