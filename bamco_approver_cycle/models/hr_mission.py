from odoo import fields, api, models, _

from datetime import datetime, time

from dateutil import rrule
from odoo.http import request

from odoo.exceptions import ValidationError


class HrMission(models.Model):
    _inherit = 'hr.mission'

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

    employee_id = fields.Many2one('hr.employee',domain=domain_employee_manager)


    def action_approve(self):
        res = super(HrMission, self).action_approve()
        users = self.env['res.users'].search([])
        for user in users:
            if user.has_group('bamco_access_groups_and_rules.group_approve_request_hr'):
                notification_ids = [(0, 0, {
                    'res_partner_id': user.partner_id.id,
                    'notification_type': 'inbox'})]
                self.message_post(record_name='Mission Request Approved',
                                  body=""" Mission Request from employee has been Approved by: """ + self.env.user.partner_id.name + """
                                                                      <br> You can access mission details from here: <br>"""
                                       + """<a href=%s>Link</a>""" % (
                                           self.leave_excuse_page())
                                  , message_type="notification",
                                  subtype_xmlid="mail.mt_comment",
                                  author_id=self.env.user.partner_id.id,
                                  notification_ids=notification_ids)
            # else:
            #     raise ValidationError(_('Only Employee Adminstrator can approve '))

        return res


    def leave_mission_page(self):
        menu_id = self.env.ref('bamco_hr_self_service.menu_hr_mission').sudo()
        action_id = self.env.ref('bamco_hr_self_service.action_hr_mission').sudo()
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        base_url += '&menu_id=%d&action=%d' % (menu_id.id, action_id.id)
        return base_url

    @api.model
    def create(self, vals):
        res = super(HrMission, self).create(vals)
        res.notify_mission()
        return res

    def notify_mission(self):
        emps = self.env['hr.employee'].search([('id', '=', self.employee_id.id)])
        users = self.env['res.users'].search([])
        for emp in emps:
            if emp.parent_id:
                notification_ids = [(0, 0, {
                    'res_partner_id': emp.parent_id.user_id.partner_id.id,
                    'notification_type': 'inbox'})]
                self.message_post(record_name='Mission Request',
                                  body=""" Mission Request from employee: """ + self.env.user.partner_id.name + """
                                                       <br> You can access mission details from here: <br>"""
                                       + """<a href=%s>Link</a>""" % (
                                           self.leave_mission_page())
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
                        self.message_post(record_name='Mission Request',
                                          body=""" Mission Request from employee: """ + self.env.user.partner_id.name + """
                                                               <br> You can access mission details from here: <br>"""
                                               + """<a href=%s>Link</a>""" % (
                                                   self.leave_mission_page())
                                          , message_type="notification",
                                          subtype_xmlid="mail.mt_comment",
                                          author_id=self.env.user.partner_id.id,
                                          notification_ids=notification_ids)


