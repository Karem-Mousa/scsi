# -*- coding: utf-8 -*-

from odoo import models, fields, api


class AdminRequest(models.Model):
    _name = 'admin.request'
    _inherit = ['admin.request', 'main.approve.model']

    def print_report(self):
        action = self.env.ref('bamco_admin_req_report.admin_req_report').report_action(self)
        return action
