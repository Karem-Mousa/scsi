# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
from dateutil import relativedelta
from odoo.http import request
from odoo.exceptions import ValidationError
from lxml import etree




class HrAppraisal(models.Model):
    _inherit = 'hr.appraisal'

    kpi_id = fields.Many2one('kpi.appraisal','KPI')
    is_hr = fields.Boolean(compute='compute_is_hr')
    is_manager = fields.Boolean(compute='compute_is_manager')
    is_manager_button = fields.Boolean()
    is_hr_button = fields.Boolean()

    recomndetions = fields.Text('التوصيات')

    hr_appraisal_line = fields.One2many('hr.appraisal.line', 'hr_kpi_id')
    manager_appraisal_line = fields.One2many('manager.appraisal.line', 'manager_kpi_id')

    total_manager_appraisal = fields.Float(compute='compute_total_manager_appraisal',store=True)
    total_hr_appraisal = fields.Float(compute='compute_total_hr_appraisal',store=True)
    total_manager_hr_appraisal = fields.Float(compute='compute_total_manager_hr_appraisal',store=True,string='Total Appraisal')

    attend_id = fields.Char(related='employee_id.attendance_id',string='Attendance ID')

    def create_remaning_lines(self):
        for rec in self:
            manager_values = []
            if len(rec.manager_appraisal_line) > len(rec.hr_appraisal_line):
                manager = list(rec.manager_appraisal_line.ids)
                hr = list(rec.hr_appraisal_line.ids)
                manager_new_list = manager[len(hr):]
                manager_browse = self.env['manager.appraisal.line'].browse(manager_new_list)
                for m in manager_browse:
                    manager_dict = {
                        'employee_id': rec.employee_id.id,
                        'attendance_id': rec.attend_id,
                        'date_close': rec.date_close,
                        'department_id': rec.department_id.id,
                        'kpi_id': rec.kpi_id.id,
                        'manager_question': m.question if m.question else '',
                        'manager_evaluation': m.mark_added if m.mark_added else 0,
                    }
                    manager_values.append(manager_dict)
                return manager_values


    def button_done_appraisal(self):
        res = super(HrAppraisal, self).button_done_appraisal()
        m_h_values = []
        for rec in self:
            for m in rec.manager_appraisal_line:
                for h in rec.hr_appraisal_line:
                    if list(rec.manager_appraisal_line).index(m) == list(rec.hr_appraisal_line).index(h):
                        values = {
                            'employee_id': rec.employee_id.id,
                            'attendance_id': rec.attend_id,
                            'date_close': rec.date_close,
                            'department_id': rec.department_id.id,
                            'kpi_id': rec.kpi_id.id,
                            'manager_question': m.question if m.question else '',
                            'manager_evaluation': m.mark_added if m.mark_added else 0,
                            'hr_question': h.question if h.question else '',
                            'hr_evaluation': h.mark_added if h.mark_added else 0,
                        }
                        m_h_values.append(values)
                        break
            hr_manager = m_h_values
            remaining = self.create_remaning_lines()
            self.env['appraisal.data'].create(hr_manager)
            if remaining:
                self.env['appraisal.data'].create(remaining)
        return res



    @api.onchange('kpi_id')
    def onchange_kpi_yearly_evaluate(self):
        # if self.kpi_id.monthly_evaluation != True:
        if self.manager_appraisal_line or self.hr_appraisal_line:
            self.manager_appraisal_line = None
            self.hr_appraisal_line = None
        manager_lines = []
        hr_lines = []
        for line in self.kpi_id.manager_appraisal_line:
            manager_lines.append((0, 0, {
                'question': line.question,
                'full_mark': line.full_mark,
                'mark_added': line.mark_added,
            }))
        for line in self.kpi_id.hr_appraisal_line:
            hr_lines.append((0, 0, {
                'question': line.question,
                'full_mark': line.full_mark,
                'mark_added': line.mark_added,
            }))
        self.manager_appraisal_line = manager_lines
        self.hr_appraisal_line = hr_lines
        # else:
        #     self.manager_appraisal_line = None
        #     self.hr_appraisal_line = None

    def print_evaluation(self):
        if self.kpi_id.monthly_evaluation == True:
            return self.env.ref('centione_employee_appraisal.monthly_appraisal_report').sudo().report_action(docids=self.ids)
        else:
            return self.env.ref('centione_employee_appraisal.yearly_appraisal_report').sudo().report_action(docids=self.ids)

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(HrAppraisal, self).get_view(view_id=view_id, view_type=view_type,**options)
        doc = etree.XML(res['arch'])
        if not self.env.user.has_group('centione_employee_appraisal.group_appraisal_hr'):
            if view_type == 'form':
                nodes = doc.xpath("//form[@string='Appraisal']")
                for node in nodes:
                    node.set('create', '0')
                    node.set('delete', '0')
                res['arch'] = etree.tostring(doc)
        return res

    @api.depends('manager_appraisal_line.mark_added')
    def compute_total_manager_appraisal(self):
        for rec in self:
            total_marks = 0
            full_marks = 0
            for line in rec.manager_appraisal_line:
                total_marks += line.mark_added
                full_marks += line.full_mark
            if full_marks > 0:
                rec.total_manager_appraisal = (total_marks / full_marks) * 100
            else:
                rec.total_manager_appraisal = (total_marks / 100) * 100

    @api.depends('hr_appraisal_line.mark_added')
    def compute_total_hr_appraisal(self):
        for rec in self:
            hr_total_marks = 0
            hr_full_marks = 0
            for line in rec.hr_appraisal_line:
                hr_total_marks += line.mark_added
                hr_full_marks += line.full_mark
            if hr_full_marks > 0:
                rec.total_hr_appraisal = (hr_total_marks / hr_full_marks) * 100
            else:
                rec.total_hr_appraisal = (hr_total_marks / 100) * 100

    @api.depends('total_manager_appraisal','total_hr_appraisal')
    def compute_total_manager_hr_appraisal(self):
        for rec in self:
            total_manager_appraisal = sum([m.mark_added for m in rec.manager_appraisal_line])
            total_hr_appraisal = sum([h.mark_added for h in rec.hr_appraisal_line])
            total_manager_hr_appraisal = (total_manager_appraisal + total_hr_appraisal) / 100
            rec.total_manager_hr_appraisal = total_manager_hr_appraisal * 100

    def compute_is_hr(self):
        if self.env.user.has_group('centione_employee_appraisal.group_appraisal_hr'):
            self.is_hr = True
        else:
            self.is_hr = False

    def compute_is_manager(self):
        if self.env.user.id == self.employee_id.parent_id.user_id.id:
            self.is_manager = True
        else:
            self.is_manager = False

    def leave_page(self):
        menu_id = self.env.ref('hr_appraisal.menu_open_view_hr_appraisal_tree')  # menu id
        action_id = self.env.ref('hr_appraisal.open_view_hr_appraisal_tree')  # action id
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&amp;view_type=form&amp;model=%s' % (self.id, self._name)
        base_url += '&amp;menu_id=%d&amp;action=%d' % (menu_id.id, action_id.id)
        return base_url

    def leave_page_manager(self):
        action_id = self.env.ref('centione_employee_appraisal.second_menu_action_appraisal')  # action id
        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#&amp;view_type=list&amp;model=%s' % (self._name)
        base_url += '&amp;action=%d' % (action_id.id)
        return base_url

    def manager_notify(self):
        if self.employee_id.coach_id.user_id:
            self.is_manager_button = True
            notification_ids = [(0, 0, {
                'res_partner_id': self.sudo().employee_id.coach_id.user_id.partner_id.id,
                'notification_type': 'inbox'
            })]
            self.sudo().message_post(record_name='Appraisal',
                              body=""" Appraisal For Employee: """ + self.sudo().employee_id.name + """
                                                         <br> You can access appraisal details from here: <br>"""
                                   + """<a href="%s">Link</a>""" % (
                                       self.sudo().leave_page_manager())
                              , message_type="notification",
                              subtype_xmlid="mail.mt_comment",
                              author_id=self.sudo().env.user.partner_id.id,
                              notification_ids=notification_ids)
    def hr_notify(self):
        partners = self.env['res.users'].search(
            [('groups_id', 'in', [self.env.ref('centione_employee_appraisal.group_appraisal_hr').id])])
        self.is_hr_button = True
        for partner in partners:
            notification_ids = [(0, 0, {
                'res_partner_id': partner.partner_id.id,
                'notification_type': 'inbox'
            })]
            self.message_post(record_name='Appraisal Evaluated by Manager' + ' ' + self.employee_id.coach_id.name,
                              body=""" Appraisal For Employee: """ + self.employee_id.name + """
                                                                     <br> You can access appraisal details from here: <br>"""
                                   + """<a href="%s">Link</a>""" % (
                                       self.leave_page())
                              , message_type="notification",
                              subtype_xmlid="mail.mt_comment",
                              author_id=self.env.user.partner_id.id,
                              notification_ids=notification_ids)


class ManagerAppraisalLine(models.Model):
    _name = 'manager.appraisal.line'

    manager_kpi_id = fields.Many2one('hr.appraisal')
    question = fields.Char('Question',readonly=True)
    full_mark = fields.Float('Full Mark',readonly=True)
    mark_added = fields.Float('Evaluation')

    @api.constrains('mark_added')
    def constrain_mark_added(self):
        for rec in self:
            if rec.mark_added > rec.full_mark:
                raise ValidationError("Cannot Exceed Full Mark")



class HrAppraisalLine(models.Model):
    _name = 'hr.appraisal.line'

    hr_kpi_id = fields.Many2one('hr.appraisal')
    question = fields.Char('Question',readonly=True)
    full_mark = fields.Float('Full Mark',readonly=True)
    mark_added = fields.Float('Evaluation')


    @api.constrains('mark_added')
    def constrain_mark_added(self):
        for rec in self:
            if rec.mark_added > rec.full_mark:
                raise ValidationError("Cannot Exceed Full Mark")

