from odoo import fields, api, models, _
from dateutil import relativedelta


from datetime import datetime, time

from dateutil import rrule
from odoo.http import request

from odoo.exceptions import ValidationError


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['hr.loan','hr.mail.service']
    # _inherits = {'hr.mail.service':'mail_service_id'}


    def domain_employee_manager(self):
        domain = []
        if not self.env.user.has_group('hr.group_hr_manager'):
            domain.append(('|'))
            domain.append(('|'))
            domain.append(('|'))
            domain.append(('|'))
            domain.append(('user_id','=',self.env.user.id))
            domain.append(('parent_id.user_id','=',self.env.user.id))
            domain.append(('parent_id.parent_id.user_id','=',self.env.user.id))
            domain.append(('parent_id.parent_id.parent_id.user_id','=',self.env.user.id))
            domain.append(('parent_id.parent_id.parent_id.parent_id.user_id','=',self.env.user.id))
        return domain

    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,domain=domain_employee_manager,track_visibility='always')
    is_approve = fields.Boolean(comupte='compute_is_approve')
    comment = fields.Text(default='أتعهد أنا الموظف بأننى ملتزم بسداد السلفة من أجورى الشهرية على أن يتم خصم مبلغ السلفة المذكورة أعلاه وفى حالة الاستقالة أو انهاء عقد العمل فيحق لشركة التميز لحلول الأعمال خصم مبلغ السلفة من بدل الاجازة أو نهاية الخدمة .  I, the employee, pledge that I am committed to paying the advance from my monthly wages, provided that the amount of the advance mentioned above is deducted in the event of resignation or termination of the work contract. The Baqader Trading Company has the right to deduct the amount of the advance from the leave allowance or end of service.')
    done_payment_date = fields.Date('Payment Done')
    user_done = fields.Char('User')
    # mail_service_id = fields.Many2one('hr.mail.service', required=True, ondelete="cascade")

    @api.onchange('loan_type')
    def employee_id_domain(self):
        long_term_employee = []
        employees = self.env['hr.contract'].sudo().search([])
        if self.loan_type == 'long_term':
            for emp in employees:
                diff = relativedelta.relativedelta(emp.date_end, emp.date_start).years
                if diff > 1 and emp.employee_id.id not in long_term_employee:
                    long_term_employee.append(emp.employee_id.id)
        else:
            for emp in employees:
                if emp.employee_id.id not in long_term_employee:
                    long_term_employee.append(emp.employee_id.id)
        return {'domain': {'employee_id': [('id', 'in', long_term_employee)]}}
        # self.employee_id = long_term_employee


    def compute_is_approve(self):
        for rec in self:
            if self.env.user.has_group('bamco_access_groups_and_rules.group_approve_request_hr'):
                rec.is_approve = True
            else:
                rec.is_approve = False



    def loan_page(self):
        menu_id = self.env.ref('bamco_hr_loan_correct.menu_view_loan').sudo()
        action_id = self.env.ref('bamco_hr_loan_correct.action_loan_tree_view').sudo()
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        base_url += '&menu_id=%d&action=%d' % (menu_id.id, action_id.id)
        return base_url

    def send_link_to_mail(self,employee):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)

        msg_body = """
                            Dear {},
                            <br/>
                            Your <a href={}</a> Loan is available
                        """.format(employee.name, base_url)
        return msg_body

    @api.model
    def create(self, vals):
        res = super(HrLoan, self).create(vals)
        message = res.send_link_to_mail(res.employee_id)
        subject = 'Loan'
        res.notify_loan()
        res.sudo().send_email_to_hr(message, res.employee_id.parent_id.work_email, subject,)
        return res

    def notify_loan(self):
        users = self.env['res.users'].search([])
        for user in users:
            if user.has_group('bamco_access_groups_and_rules.group_approve_request_hr'):
                notification_ids = [(0, 0, {
                    'res_partner_id': user.partner_id.id,
                    'notification_type': 'inbox'})]
                self.message_post(record_name='Loan Request',
                                  body=""" Loan Request from employee: """ + self.env.user.name + """
                                                               <br> You can access loan details from here: <br>"""
                                       + """<a href=%s>Link</a>""" % (
                                           self.loan_page())
                                  , message_type="notification",
                                  subtype_xmlid="mail.mt_comment",
                                  author_id=self.env.user.partner_id.id,
                                  notification_ids=notification_ids)
