# -*- coding: utf-8 -*-
# Part of BrowseInfo. See LICENSE file for full copyright and licensing details.
##############################################################################

import json
import base64
import odoo.http as http
from odoo.http import request
from odoo.addons.portal.controllers.portal import CustomerPortal, pager as portal_pager
from odoo import fields



class WebsiteVendorRegistration(CustomerPortal):

    @http.route(['/vendor_req'], type='http', auth="public", website=True)
    def vendor_registration_req(self, **kw):
        name = ""
        if http.request.env.user.name != "Public user":
            name = http.request.env.user.name

        email = http.request.env.user.partner_id.email
        phone = http.request.env.user.partner_id.phone
        values = {'user_ids': name, 'email': email, 'phone': phone}

        return request.render("bi_vendor_registration_request.bi_vendor_registration_req", values)

    @http.route('/vendor_req/thankyou', type="http", auth="public", website=True)
    def vendor_registration_req_thankyou(self, **post):
        if post.get('debug'):
            return request.render("bi_vendor_registration_request.bi_vendor_registration_thank_you")
        if post:
            vals = {
                'name': post['user_ids'],
                'email': post['email_from'],
                'phone': post['phone'],
                'mobile': post['mobile'],
                'street': post['street'],
                'city': post['city'],
                'zip': post['zipcode'],
                'link': post['link'],
                'country': post['country_id'],
                'state_id': post['state_id'],
                'state': 'to_approve',
                'type': post.get('type'),
                'vat': post.get('vat'),
                'commercial_register_date': post.get('commercial_register_date') if post.get('commercial_register_date') else fields.Date.today(),
                'commercial_register_num': post.get('commercial_register_num'),
                'commercial_chamber_certificate_date': post.get('commercial_chamber_certificate_date') if post.get('commercial_chamber_certificate_date') else fields.Date.today(),
                'commercial_chamber_certificate_num': post.get('commercial_chamber_certificate_num'),
                'zakat_certificate_date': post.get('zakat_certificate_date') if post.get('zakat_certificate_date') else fields.Date.today(),
                'zakat_certificate_num': post.get('zakat_certificate_num'),
                'social_insurance_certificate_date': post.get('social_insurance_certificate_date') if post.get('social_insurance_certificate_date') else fields.Date.today(),
                'social_insurance_certificate_num': post.get('social_insurance_certificate_num'),
                'saudization_certificate_date': post.get('saudization_certificate_date') if post.get('saudization_certificate_date') else fields.Date.today(),
                'saudization_certificate_num': post.get('saudization_certificate_num'),
                'iban_bank': post.get('iban_bank'),
                'iban_number': post.get('iban_number')
            }
            vendor_req_obj = request.env['vendor.registration.request'].sudo().create(vals)
            if vendor_req_obj.type == 'company':
                child1_vals = {
                    'name': post.get('child_ids1'),
                    'email': post.get('email_from1'),
                    'phone': post.get('phone1'),
                }
                vendor_req_obj.update({'child_ids': [(0, 0, child1_vals)]})
                child2_vals = {
                    'name': post.get('child_ids2'),
                    'email': post.get('email_from2'),
                    'phone': post.get('phone2'),
                }
                vendor_req_obj.update({'child_ids': [(0, 0, child2_vals)]})
            file = request.httprequest.files.getlist('file')
            if file:
                for i in range(len(file)):
                    vendor_req_obj.write({'vendor_image': base64.b64encode(file[i].read())})

            commercial_register = request.httprequest.files.getlist('commercial_register')
            if commercial_register:
                for i in range(len(commercial_register)):
                    vendor_req_obj.write({'commercial_register': base64.b64encode(commercial_register[i].read())})

            commercial_chamber_certificate = request.httprequest.files.getlist('commercial_chamber_certificate')
            if commercial_chamber_certificate:
                for i in range(len(commercial_chamber_certificate)):
                    vendor_req_obj.write(
                        {'commercial_chamber_certificate': base64.b64encode(commercial_chamber_certificate[i].read())})

            zakat_certificate = request.httprequest.files.getlist('zakat_certificate')
            if zakat_certificate:
                for i in range(len(zakat_certificate)):
                    vendor_req_obj.write({'zakat_certificate': base64.b64encode(zakat_certificate[i].read())})

            social_insurance_certificate = request.httprequest.files.getlist('social_insurance_certificate')
            if social_insurance_certificate:
                for i in range(len(social_insurance_certificate)):
                    vendor_req_obj.write(
                        {'social_insurance_certificate': base64.b64encode(social_insurance_certificate[i].read())})

            saudization_certificate = request.httprequest.files.getlist('saudization_certificate')
            if saudization_certificate:
                for i in range(len(saudization_certificate)):
                    vendor_req_obj.write(
                        {'saudization_certificate': base64.b64encode(saudization_certificate[i].read())})

            tax_certificate = request.httprequest.files.getlist('tax_certificate')
            if tax_certificate:
                for i in range(len(tax_certificate)):
                    vendor_req_obj.write(
                        {'tax_certificate': base64.b64encode(tax_certificate[i].read())})

            iban_certificate = request.httprequest.files.getlist('iban_certificate')
            if iban_certificate:
                for i in range(len(iban_certificate)):
                    vendor_req_obj.write(
                        {'iban_certificate': base64.b64encode(iban_certificate[i].read())})

        return request.render("bi_vendor_registration_request.bi_vendor_registration_thank_you")

    @http.route(['/my/state/<model("res.country"):country>'], type='json', auth="public", methods=['POST'],
                website=True)
    def country_infos(self, country, **kw):
        return dict(
            fields=country.get_address_fields(),
            states=[(st.id, st.name, st.code) for st in country.get_country_states()],
            phone_code=country.phone_code
        )
