from odoo import models, fields, api, _
from odoo.exceptions import UserError


class AbstractModel(models.AbstractModel):
    _name = 'hr.mail.service'

    def send_email_to_hr(self, message, approver_email, subject):
        try:
            Mail = self.env['mail.mail']
            outgoing_mail = self.env['ir.mail_server'].search([], limit=1)
            if not outgoing_mail or not outgoing_mail.smtp_port or not outgoing_mail.smtp_user or not outgoing_mail.smtp_pass:
                raise UserError(
                    _('Outgoing email should be configured well,please contact us!'))

            # mail values
            mail_values = {
                'subject': subject,
                'author_id': 1,
                'email_from': '<' + outgoing_mail.smtp_user + '>',
                'email_to': approver_email,
                'body_html': message,
                # 'attachment_ids': [(0, 0, {'name': i['name'],
                #                            'datas': i['datas']}) for i in attachments],
            }

            # create mail, that will create it in odoo mails
            created_mail = Mail.create(mail_values)

            # send mail
            created_mail.send()

            return "sent"
        except Exception as e:
            return str(e)



