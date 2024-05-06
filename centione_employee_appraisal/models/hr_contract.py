# -*- coding: utf-8 -*-

from odoo import models, fields, api
from datetime import date
from dateutil import relativedelta
from odoo.http import request
from lxml import etree

class HrContract(models.Model):
    _inherit = 'hr.contract'

    hire_date = fields.Date('Hire Date')

    def get_view(self, view_id=None, view_type='form', **options):
        res = super(HrContract, self).get_view(view_id=view_id, view_type=view_type, **options)
        doc = etree.XML(res['arch'])
        if self.env.user.has_group('centione_employee_appraisal.group_see_contracts_emps'):
                nodes = doc.xpath("//form[@string='Current Contract']")
                for node in nodes:
                    node.set('create', '0')
                    node.set('delete', '0')
                res['arch'] = etree.tostring(doc)
        return res