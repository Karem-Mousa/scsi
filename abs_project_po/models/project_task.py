# -*- coding: utf-8 -*-
from odoo import api, fields, models, _


class Project(models.Model):
    _inherit = 'project.task'

    purchase_order_ids = fields.One2many('purchase.order', 'project_id', string="Purchase Orders")

    def action_new_rfq(self):
        action = self.env["ir.actions.actions"]._for_xml_id("abs_project_po.purchase_action_rfq_new")


        action['context'] = {
            'default_project_id': self.project_id.id,
            'default_task_id': self.id,

        }
        return action