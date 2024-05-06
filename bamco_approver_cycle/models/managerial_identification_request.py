from odoo import models, fields, api, _
from odoo.exceptions import UserError


class ManagerialIdentificationRequest(models.AbstractModel):
    _name = 'managerial.identification.request'
    _inherit = ['managerial.identification.request', 'hr.mail.service']

    def send_link_to_mail(self, employee):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        msg_body = """
                                Dear {},
                                <br/>
                                Your <a href={}>طلب التعريف الإداري is available</a> 
                            """.format(employee.name, base_url)

        return msg_body

    @api.model
    def create(self, vals):
        res = super(ManagerialIdentificationRequest, self).create(vals)
        message = res.send_link_to_mail(res.employee_id)
        subject = 'طلب التعريف الإداري'
        res.sudo().send_email_to_hr(message, res.employee_id.parent_id.work_email, subject, )
        return res

    def action_approve(self):
        res = super(ManagerialIdentificationRequest, self).action_approve()
        subject = 'طلب التعريف الإداري'
        employees = self.env.ref('bamco_emp_service_cycle_approve.validation_group').users.mapped('employee_ids')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        msg_body = """
                                             Dear {},
                                             <br/>
                                             Your <a href={}>طلب التعريف الإداري is {}</a> 
                                         """.format(self.employee_id.name, base_url, self.state)
        for rec in employees:
            self.sudo().send_email_to_hr(msg_body, rec.work_email, subject, )
        return res
