# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
from dateutil import relativedelta
from odoo.http import request
from lxml import etree

class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    hire_date = fields.Date('Hire Date')
    attendance_id = fields.Char('Attendance ID')

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(HrEmployee, self).get_view(view_id=view_id, view_type=view_type, **options)
        doc = etree.XML(res['arch'])
        if self.env.user.has_group('centione_employee_appraisal.group_see_contracts_emps'):
                nodes = doc.xpath("//form[@string='Employee']")
                for node in nodes:
                    node.set('create', '0')
                    node.set('edit', '0')
                    node.set('delete', '0')
                res['arch'] = etree.tostring(doc)
        return res
    def create_appraisal_employee(self,employee,date_close):
        employee = employee
        date_close = date_close
        kpi = self.env['kpi.appraisal'].search([('monthly_evaluation','=',True)],limit=1)
        manager_kpi = []
        hr_kpi = []
        for line in kpi.manager_appraisal_line:
            manager_kpi.append((0, 0, {
                'question': line.question,
                'full_mark': line.full_mark,
                'mark_added': line.mark_added,
            }))
        for line in kpi.hr_appraisal_line:
            hr_kpi.append((0, 0, {
                'question': line.question,
                'full_mark': line.full_mark,
                'mark_added': line.mark_added,
            }))
        values = {
            'employee_id' : employee,
            'date_close' : date_close,
            'kpi_id' : kpi.id,
            'manager_appraisal_line' : manager_kpi,
            'hr_appraisal_line' : hr_kpi,
        }

        return values

    def leave_page(self):
        menu_id = self.env.ref('hr_appraisal.menu_open_view_hr_appraisal_tree')  # menu id
        action_id = self.env.ref('hr_appraisal.open_view_hr_appraisal_tree')  # action id
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&amp;view_type=list&amp;model=%s' % (self.id, self._name)
        base_url += '&amp;menu_id=%d&amp;action=%d' % (menu_id.id, action_id.id)
        return base_url

    def hire_date_monthly_notify(self):
        employees = self.search([])
        partners = self.env['res.users'].search(
            [('groups_id', 'in', [self.env.ref('centione_employee_appraisal.group_appraisal_hr').id])])
        for emp in employees:
            if emp.hire_date:
                delta = relativedelta.relativedelta(date.today(), emp.hire_date)
                if delta.months == 3:
                    for partner in partners:
                        notification_ids = [(0, 0, {
                            'res_partner_id': partner.partner_id.id,
                            'notification_type': 'inbox'
                        })]
                        self.message_post(record_name='Appraisal Created',
                                          body=""" Appraisal For Employee: """ + emp.name + """
                                             <br> You can access appraisal details from here: <br>"""
                                               + """<a href="%s">Link</a>""" % (
                                                   self.leave_page())
                                          , message_type="notification",
                                          subtype_xmlid="mail.mt_comment",
                                          author_id=self.env.user.partner_id.id,
                                          notification_ids=notification_ids)
                    appraisial = self.sudo().create_appraisal_employee(emp.id,date.today())
                    self.env['hr.appraisal'].sudo().create(appraisial)













