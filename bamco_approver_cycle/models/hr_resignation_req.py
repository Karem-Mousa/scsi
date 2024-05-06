from odoo import models, fields, api, _
from odoo.exceptions import UserError


class HrResignationReq(models.AbstractModel):
    _name = 'hr.resignation.req'
    _inherit = ['hr.resignation.req', 'hr.mail.service']

    def send_link_to_mail(self, employee):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        msg_body = """
                                   Dear {},
                                   <br/>
                                   Your <a href={}>طلب استقالة is available</a>
                               """.format(employee.name, base_url)

        return msg_body

    @api.model
    def create(self, vals):
        res = super(HrResignationReq, self).create(vals)
        message = res.send_link_to_mail(res.employee_id)
        subject = 'طلب استقالة'
        res.sudo().send_email_to_hr(message, res.employee_id.parent_id.work_email, subject, )
        return res

    def action_approve(self):
        res = super(HrResignationReq, self).action_approve()
        subject = 'طلب استقالة'
        employees = self.env.ref('bamco_emp_service_cycle_approve.validation_group').users.mapped('employee_ids')
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        msg_body = """
                                                Dear {},
                                                <br/>
                                                Your <a href={}>طلب استقالة is {}</a> 
                                            """.format(self.employee_id.name, base_url, self.state)
        for rec in employees:
            self.sudo().send_email_to_hr(msg_body, rec.work_email, subject, )
        return res
