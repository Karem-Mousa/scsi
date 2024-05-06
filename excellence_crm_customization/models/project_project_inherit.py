from odoo import models, fields, api, tools, _


class ExcProjectInherit(models.Model):
    _inherit = "project.project"

    x_project_name = fields.Char(string="Project Name")


