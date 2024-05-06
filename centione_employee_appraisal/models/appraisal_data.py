# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
from dateutil import relativedelta
from odoo.http import request
from odoo.exceptions import ValidationError
from lxml import etree




class AppraisalData(models.Model):
    _name = 'appraisal.data'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee','Employee')
    attendance_id = fields.Char('Attendance ID')
    date_close = fields.Date('Appraisal Deadline')
    manager_question = fields.Char('Manager Question')
    manager_evaluation = fields.Float('Manager Evaluation')
    hr_question = fields.Char('Hr Question')
    hr_evaluation = fields.Float('Hr Evaluation')
    department_id = fields.Many2one('hr.department','Department')
    kpi_id = fields.Many2one('kpi.appraisal','KPI')

