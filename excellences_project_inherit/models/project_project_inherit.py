from odoo import fields, models, api, _


class EXProjectInherit(models.Model):
    _inherit = "project.project"

    achievement_certificate = fields.Binary(string='Achievement Certificate')
    project_charter = fields.Binary(string='Project Charter')
    business_certificate = fields.Binary(string='Business Certificate')
    other = fields.Binary(string='Other')
