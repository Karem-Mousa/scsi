from odoo import fields, models, api
import json
import requests


class ExcProjectInherit(models.Model):
    _inherit = "project.project"

    @api.model
    def create(self, vals):
        res = super(ExcProjectInherit, self).create(vals)

        url = 'https://portal.excellences.sa/create_project'

        headers = {
            'access-token': 'wMOjlrgIe2f4RPrlU6j4bSxjtgy',
        }
        payload = {
            "project_name": res.name,
            'x_project_name': res.x_project_name,
            'project_id': res.id,
        }
        if res.allow_billable:
            payload['billable'] = True
        if res.allow_timesheets:
            payload['time_sheets'] = True

        response = requests.request("POST", url, data=payload, headers=headers)
        if response:
            response = response.text.encode('utf8')
            response = json.loads(response.decode('utf-8'))
        return res
