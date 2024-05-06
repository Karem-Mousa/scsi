from odoo import fields, models, api
import json
import requests


class ExcProjectTaskTypeInherit(models.Model):
    _inherit = "project.task.type"

    def write(self, vals):
        if 'project_ids' in vals:
            project_ids1 = self.project_ids.ids
            res = super(ExcProjectTaskTypeInherit, self).write(vals)
            project_ids2 = self.project_ids.ids

            if len(project_ids1) < len(project_ids2):
                project_id = set(project_ids2) - set(project_ids1)

                url = 'https://portal.excellences.sa/update_project'
                headers = {
                    'access-token': 'wMOjlrgIe2f4RPrlU6j4bSxjtgy',
                }
                payload = {
                    'project_id': project_id,
                    'project_task_stage_id': self.id,
                    'stage_name': self.name
                }

                response = requests.request("POST", url, data=payload, headers=headers)
                if response:
                    response = response.text.encode('utf8')
                    response = json.loads(response.decode('utf-8'))
        return res
