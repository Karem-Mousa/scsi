from odoo import fields, models, api
import json
import requests


class ExcProjectTaskTypeInherit(models.Model):
    _inherit = "project.task.type"

    x_sci_project_task_type_id = fields.Char()
