# -*- coding: utf-8 -*-

from odoo import models, fields, api

class KpiAppraisal(models.Model):
    _name = 'kpi.appraisal'

    name = fields.Char('Name',required=True)

    monthly_evaluation = fields.Boolean('3 Months Evaluation')

    manager_appraisal_line = fields.One2many('manager.kpi.appraisal.line','manager_kpi_id')

    hr_appraisal_line = fields.One2many('hr.kpi.appraisal.line','hr_kpi_id')


class ManagerKpiAppraisalLine(models.Model):
    _name = 'manager.kpi.appraisal.line'

    manager_kpi_id = fields.Many2one('kpi.appraisal')
    question = fields.Char('Question')
    full_mark = fields.Float('Full Mark')
    mark_added = fields.Float('Evaluation')


class HrKpiAppraisalLine(models.Model):
    _name = 'hr.kpi.appraisal.line'

    hr_kpi_id = fields.Many2one('kpi.appraisal')
    question = fields.Char('Question')
    full_mark = fields.Float('Full Mark')
    mark_added = fields.Float('Evaluation')
