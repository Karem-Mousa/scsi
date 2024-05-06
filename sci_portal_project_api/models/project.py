from odoo import fields, models, api
import json
import requests


class ExcProjectInherit(models.Model):
    _inherit = "project.project"

    x_sci_project_id = fields.Char()
