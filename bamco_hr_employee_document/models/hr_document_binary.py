from datetime import date

from dateutil import relativedelta

from odoo import models, fields, api, _
from odoo.http import request


class HrDocumentBinary(models.Model):
    _name = 'hr.document.binary'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    document = fields.Binary()
    start_date = fields.Date()
    end_date = fields.Date()
    document_id = fields.Many2one('hr.document')

    def document_end_date_notify_sixty(self):
        docs = self.sudo().search([])
        users = self.env['res.users'].search([])
        docs_created = []
        for doc in docs:
            if doc.end_date:
                delta = relativedelta.relativedelta(doc.end_date, date.today())
                if delta.months == 3 and delta.days == 0 and delta.years == 0:
                    for user in users:
                        notification_ids = [(0, 0, {
                            'res_partner_id': user.partner_id.id,
                            'notification_type': 'inbox'
                        })]
                        action_id = self.env.ref('hr.open_view_employee_list_my')  # action id
                        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        base_url += '/web#id=%d&amp;view_type=form&amp' % (doc.document_id.employee_id.id)
                        base_url += '&amp;action=%d' % (action_id.id)
                        doc.message_post(record_name='Document End Date',
                                         body=""" Document Will End In 90 Days """ + ' ' +
                                              """<br> You can access employee details from here: <br>"""
                                              + """<a href="%s">Link</a>""" % (
                                                  base_url)
                                         , message_type="notification",
                                         subtype_xmlid="mail.mt_comment",
                                         author_id=user.partner_id.id,
                                         notification_ids=notification_ids,
                                         )
                elif delta.months == 1 and delta.days == 0 and delta.years == 0:
                    docs_created.append(doc.id)
                    if len(docs) == len(docs_created):
                        for user in users:
                            notification_ids = [(0, 0, {
                                'res_partner_id': user.partner_id.id,
                                'notification_type': 'inbox'
                            })]
                            action_id = self.env.ref('hr.open_view_employee_list_my')  # action id
                            base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                            base_url += '/web#id=%d&amp;view_type=form&amp' % (doc.document_id.employee_id.id)
                            base_url += '&amp;action=%d' % (action_id.id)
                            doc.message_post(record_name='Document End Date',
                                             body=""" Document Will End In 30 Days if not updated """ + ' ' +
                                                  """<br> You can access employee details from here: <br>"""
                                                  + """<a href="%s">Link</a>""" % (
                                                      base_url)
                                             , message_type="notification",
                                             subtype_xmlid="mail.mt_comment",
                                             author_id=user.partner_id.id,
                                             notification_ids=notification_ids,
                                             )
                else:
                    pass
