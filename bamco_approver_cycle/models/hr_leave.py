from odoo import fields, api, models, _

from datetime import datetime, time

from dateutil import rrule
from odoo.http import request

from odoo.exceptions import ValidationError


class HrLeaveType(models.Model):
    _inherit = 'hr.leave.type'

    not_sick_leave = fields.Boolean('Alternative Employee')

class MailNotification(models.Model):
    _inherit = 'mail.notification'

    _sql_constraints = [
        # email notification;: partner is required
        ('notification_partner_required',
         "CHECK(1=1)",
         'Customer is required for inbox / email notification'),
    ]

class MailThread(models.AbstractModel):
    _inherit = 'mail.thread'

    def _message_compute_author(self, author_id=None, email_from=None, raise_exception=True):
        """ Tool method computing author information for messages. Purpose is
        to ensure maximum coherence between author / current user / email_from
        when sending emails. """
        if author_id is None:
            if email_from:
                author = self._mail_find_partner_from_emails([email_from])[0]
            else:
                author = self.env.user.partner_id
                email_from = author.email_formatted
            author_id = author.id

        if email_from is None:
            if author_id:
                author = self.env['res.partner'].browse(author_id)
                email_from = author.email_formatted

        # superuser mode without author email -> probably public user; anyway we don't want to crash
        # if not email_from and not self.env.su and raise_exception:
        #     raise exceptions.UserError(_("Unable to log message, please configure the sender's email address."))

        return author_id, email_from

class HrLeave(models.Model):
    _name = 'hr.leave'
    _inherit = ['hr.leave', 'hr.mail.service']

    not_sick_leave_rel = fields.Boolean(related='holiday_status_id.not_sick_leave')
    identification_id_rel = fields.Char(related='employee_id.identification_id')
    attendance_id_char_rel = fields.Char(related='employee_id.attendance_id_char')
    alt_identification_id_rel = fields.Char(related='alt_employee_id.identification_id')
    alt_attendance_id_char_rel = fields.Char(related='alt_employee_id.attendance_id_char')


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

    employee_ids = fields.Many2many(
        'hr.employee', compute='_compute_from_holiday_type', store=True, string='Employees', readonly=False, groups="hr_holidays.group_hr_holidays_user,base.group_user",
        states={'cancel': [('readonly', True)], 'refuse': [('readonly', True)], 'validate1': [('readonly', True)],
                'validate': [('readonly', True)]},domain=domain_employee_manager)
    manager_approved = fields.Boolean(
        string='',
        required=False)

    is_manager = fields.Boolean(
        string='',
        required=False, compute='_compute_current_manager_user_id')

    current_manager_user_id = fields.Many2one(
        comodel_name='res.users',
        required=False, compute='_compute_current_manager_user_id')


    def _compute_current_manager_user_id(self):
        for emp in self.employee_ids:
            if self.env.user.id == emp.parent_id.user_id.id:
                self.sudo().current_manager_user_id = self.env.uid
                self.sudo().is_manager = True

            else:
                self.sudo().current_manager_user_id = False
                self.is_manager = False





    @api.constrains('employee_ids')
    def _check_employee_manager(self):
        if self.employee_ids:
            for emp in self.employee_ids:
                print('emp.user_partner_id.id', emp.parent_id.name)
                notification_ids = [(0, 0, {
                'res_partner_id': emp.parent_id.user_id.partner_id.id,
                'notification_type': 'inbox'})]
                self.message_post(record_name='Leave Request Approved',
                                  body=""" Leave Request from employee has been Creates by: """ + self.env.user.partner_id.name + """
                                                                                              <br> You can access leave details from here: <br>"""
                                       + """<a href=%s>Link</a>""" % (
                                           self.leave_page())
                                  , message_type="notification",
                                  subtype_xmlid="mail.mt_comment",
                                  author_id=self.env.user.partner_id.id,
                                  notification_ids=notification_ids)
                print('notification sended')


    def manager_approve(self):
        manager = []
        for emp in self.employee_ids:
            notification_ids = [(0, 0, {
                'res_partner_id': emp.user_partner_id.id,
                'notification_type': 'inbox'})]
            self.message_post(record_name='Leave Request Approved',
                              body=""" Leave Request from employee has been Approved by: """ + self.env.user.partner_id.name + """
                                                                                <br> You can access leave details from here: <br>"""
                                   + """<a href=%s>Link</a>""" % (
                                       self.leave_page())
                              , message_type="notification",
                              subtype_xmlid="mail.mt_comment",
                              author_id=self.env.user.partner_id.id,
                              notification_ids=notification_ids)
            self.manager_approved = True
            self.action_approve()


    def action_approve(self):
        res = super(HrLeave, self).action_approve()
        users = self.env['res.users'].search([])
        for user in users:
            if user.has_group('bamco_access_groups_and_rules.group_approve_request_hr'):
                message = self.send_link_to_mail(self.employee_id)
                subject = 'طلب اجازة'
                self.sudo().send_email_to_hr(message, self.employee_id.work_email, subject, )
                notification_ids = [(0, 0, {
                    'res_partner_id': user.partner_id.id,
                    'notification_type': 'inbox'})]
                self.message_post(record_name='Leave Request Approved',
                                  body=""" Leave Request from employee has been Approved by: """ + self.env.user.partner_id.name + """
                                                                      <br> You can access leave details from here: <br>"""
                                       + """<a href=%s>Link</a>""" % (
                                           self.leave_page())
                                  , message_type="notification",
                                  subtype_xmlid="mail.mt_comment",
                                  author_id=self.env.user.partner_id.id,
                                  notification_ids=notification_ids)

        return res


    def leave_page(self):
        menu_id = self.env.ref('hr_holidays.menu_open_department_leave_approve').sudo()
        action_id = self.env.ref('hr_holidays.hr_leave_action_action_approve_department').sudo()
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        base_url += '&menu_id=%d&action=%d' % (menu_id.id, action_id.id)
        return base_url

    def send_link_to_mail(self, employee):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        msg_body = """
                                   Dear {},
                                   <br/>
                                   Your <a href={}>طلب اجازة is available</a> 
                               """.format(employee.name, base_url)

        return msg_body

    @api.model
    def create(self, vals):
        res = super(HrLeave, self).create(vals)
        message = res.send_link_to_mail(res.employee_id)
        subject = 'طلب اجازة'
        res.sudo().send_email_to_hr(message, res.employee_id.parent_id.work_email, subject, )
        res.notify_leave()
        return res

    def notify_leave(self):
        emps = self.env['hr.employee'].search([('id', 'in', self.employee_ids.ids)])
        users = self.env['res.users'].search([])
        for emp in emps:
            if emp.parent_id:
                notification_ids = [(0, 0, {
                    'res_partner_id': emp.parent_id.user_id.partner_id.id,
                    'notification_type': 'inbox'})]
                self.message_post(record_name='Leave Request',
                                  body=""" Leave Request from employee: """ + self.env.user.partner_id.name + """
                                                       <br> You can access leave details from here: <br>"""
                                       + """<a href=%s>Link</a>""" % (
                                           self.leave_page())
                                  , message_type="notification",
                                  subtype_xmlid="mail.mt_comment",
                                  author_id=self.env.user.partner_id.id,
                                  notification_ids=notification_ids)
            else:
                for user in users:
                    if user.has_group('bamco_access_groups_and_rules.group_approve_request_hr'):
                        notification_ids = [(0, 0, {
                            'res_partner_id': user.partner_id.id,
                            'notification_type': 'inbox'})]
                        self.message_post(record_name='Leave Request',
                                          body=""" Leave Request from employee: """ + self.env.user.partner_id.name + """
                                                               <br> You can access leave details from here: <br>"""
                                               + """<a href=%s>Link</a>""" % (
                                                   self.leave_page())
                                          , message_type="notification",
                                          subtype_xmlid="mail.mt_comment",
                                          author_id=self.env.user.partner_id.id,
                                          notification_ids=notification_ids)


