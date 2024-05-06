# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.

from odoo import models, fields, _


class VendorRegistrationRequest(models.Model):
    _name = "vendor.registration.request"

    name = fields.Char("Name")
    email = fields.Char("Email")
    phone = fields.Char("Phone")
    mobile = fields.Char("Mobile")
    street = fields.Char("Street")
    city = fields.Char("City")
    zip = fields.Char("ZipCode")
    link = fields.Char("Website Link")
    country = fields.Many2one('res.country', "Country", readonly=True)
    state_id = fields.Many2one('res.country.state', string='State')
    state_city = fields.Char("State")
    state = fields.Selection([('to_approve', 'To Approve'), ('approve', 'Approved'), ('reject', 'Rejected')],
                             string='Status', default='to_approve')
    type = fields.Selection([('individual', 'Individual'), ('company', 'Company')], string='Vendor type')
    vendor_image = fields.Image("Image")
    child_ids = fields.One2many('vendor.child', 'parent_id', string="Contacts")
    vendor_id = fields.Many2one('res.partner', string="Vendor")
    vat = fields.Char("Vat")
    iban_number = fields.Char("IBAN Number")

    commercial_register = fields.Image(string='Commercial Register')
    commercial_register_date = fields.Date(string='Commercial Register Date')
    commercial_register_num = fields.Char(string='Commercial Register Number')

    commercial_chamber_certificate = fields.Image(string='Commercial Chamber Certificate')
    commercial_chamber_certificate_date = fields.Date(string='Commercial Chamber Certificate Date')
    commercial_chamber_certificate_num = fields.Char(string='Commercial Chamber Certificate Number')

    zakat_certificate = fields.Image(string='Zakat Certificate')
    zakat_certificate_date = fields.Date(string='Zakat Certificate Date')
    zakat_certificate_num = fields.Char(string='Zakat Certificate Number')

    social_insurance_certificate = fields.Image(string='Social Insurance Certificate')
    social_insurance_certificate_date = fields.Date(string='Social Insurance Certificate Date')
    social_insurance_certificate_num = fields.Char(string='Social Insurance Certificate Number')

    saudization_certificate = fields.Image(string='Saudization Certificate')
    saudization_certificate_date = fields.Date(string='Saudization Certificate Date')
    saudization_certificate_num = fields.Char(string='Saudization Certificate Number')

    tax_certificate = fields.Image(string='Tax Certificate')
    iban_certificate = fields.Image(string='IBAN Certificate')
    iban_bank = fields.Many2one('excellence.bank')

    def action_vendor_view(self):
        self.ensure_one()
        for rec in self:
            if rec.vendor_id:
                return {
                    'name': _('Vendor'),
                    'type': 'ir.actions.act_window',
                    'view_type': 'form',
                    'view_mode': 'form',
                    'res_model': 'res.partner',
                    'res_id': rec.vendor_id.id,
                }

    def create_vendor(self):
        self.state = 'approve'
        template_id = self.env.ref('bi_vendor_registration_request.create_vendor_email_template').id
        template = self.env['mail.template'].browse(template_id)
        template.send_mail(self.id, force_send=True)
        is_company = False
        if self.type == 'company':
            is_company = True
        if self.name:
            vals = {
                'name': self.name,
                'email': self.email,
                'phone': self.phone,
                'mobile': self.mobile,
                'street': self.street,
                'city': self.city,
                'zip': self.zip,
                'website': self.link,
                'country_id': self.country.id,
                'state_id': self.state_id.id,
                'image_1920': self.vendor_image,
                'is_company': is_company,
                'vat': self.vat,
                'x_iban_number': self.iban_number,

                'x_commercial_register': self.commercial_register,
                'x_commercial_register_date': self.commercial_register_date,
                'x_commercial_register_num': self.commercial_register_num,

                'x_commercial_chamber_certificate': self.commercial_chamber_certificate,
                'x_commercial_chamber_certificate_date': self.commercial_chamber_certificate_date,
                'x_commercial_chamber_certificate_num': self.commercial_chamber_certificate_num,

                'x_zakat_certificate': self.zakat_certificate,
                'x_zakat_certificate_date': self.zakat_certificate_date,
                'x_zakat_certificate_num': self.zakat_certificate_num,

                'x_social_insurance_certificate': self.social_insurance_certificate,
                'x_social_insurance_certificate_date': self.social_insurance_certificate_date,
                'x_social_insurance_certificate_num': self.social_insurance_certificate_num,

                'x_saudization_certificate': self.saudization_certificate,
                'x_saudization_certificate_date': self.saudization_certificate_date,
                'x_saudization_certificate_num': self.saudization_certificate_num,

                'x_tax_certificate': self.tax_certificate,
                'x_iban_certificate': self.iban_certificate,
                'x_iban_bank': self.iban_bank.id
            }
            vendor_req_obj = self.env['res.partner'].sudo().create(vals)
            if is_company:
                for child in self.child_ids:
                    child_vals = {
                        'name': child.name,
                        'email': child.email,
                        'phone': child.phone,
                        'parent_id': vendor_req_obj.id,
                    }
                    self.env['res.partner'].sudo().create(child_vals)
            self.update({'vendor_id': vendor_req_obj.id})
            return vendor_req_obj


class VendorChild(models.Model):
    _name = "vendor.child"

    name = fields.Char(string="Name")
    email = fields.Char(string="Email")
    phone = fields.Char(string="phone")
    parent_id = fields.Many2one('vendor.registration.request', string="Parent")
