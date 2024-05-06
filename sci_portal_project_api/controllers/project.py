import json

from odoo import http
from odoo.http import request


class ProjectApi(http.Controller):

    @http.route(['/create_project'], type="http", auth="public", website=False, method=['POST'],
                csrf=False)
    def create_project(self, **args):
        _response = {"data": None, "itemsCount": 0, "success": True,
                     "statusCode": 400,
                     "message": "NOT EXIST"}
        try:
            access_token = request.httprequest.headers.get('access-token')
            project_id = args.get('project_id', False)
            project_name = args.get('project_name', False)
            x_project_name = args.get('x_project_name', False)
            billable = args.get('billable', False)
            time_sheets = args.get('time_sheets', False)
            if access_token:
                if access_token == 'wMOjlrgIe2f4RPrlU6j4bSxjtgy':
                    if project_name and project_id:
                        request.env['project.project'].sudo().create({
                            'name': project_name,
                            'x_project_name': x_project_name if x_project_name else '',
                            'allow_billable': True if billable else False,
                            'allow_timesheets': True if time_sheets else False,
                            'x_sci_project_id': project_id
                        })

                        _response = {"data": None, "success": True,
                                     "statusCode": 200,
                                     "message": "success"}
                    else:
                        _response = {"data": None, "itemsCount": 0, "success": False, "statusCode": 404,
                                     "message": 'Required data is missing'}

                else:
                    _response = {"data": None, "itemsCount": 0, "success": False, "statusCode": 401,
                                 "message": ' Unauthorized'}
            else:
                _response = {"data": None, "itemsCount": 0, "success": False, "statusCode": 404,
                             "message": "Access Token Is Missing"}
        except Exception as e:
            _response = {"data": None, "itemsCount": 0, "success": False, "statusCode": 400, "message": str(e)}
        finally:
            return json.dumps(_response)

    @http.route(['/update_project'], type="http", auth="public", website=False, method=['POST'],
                csrf=False)
    def update_project(self, **args):
        _response = {"data": None, "itemsCount": 0, "success": True,
                     "statusCode": 400,
                     "message": "NOT EXIST"}
        try:
            access_token = request.httprequest.headers.get('access-token')
            project_id = args.get('project_id', False)
            project_task_stage_id = args.get('project_task_stage_id', False)
            stage_name = args.get('stage_name', False)
            if access_token:
                if access_token == 'wMOjlrgIe2f4RPrlU6j4bSxjtgy':
                    if project_id:
                        project = request.env['project.project'].sudo().search([('x_sci_project_id', '=', project_id)],
                                                                               order='create_date desc', limit=1)
                        if project:
                            if project_task_stage_id:
                                project_task_type = request.env['project.task.type'].sudo().search([
                                    ('x_sci_project_task_type_id', '=', project_task_stage_id)],
                                    order='create_date desc', limit=1)
                                if not project_task_type:
                                    project_task_type = request.env['project.task.type'].sudo().create({
                                        'name': stage_name,
                                        'x_sci_project_task_type_id': project_task_type.id
                                    })
                                if project_task_type:
                                    if project_task_type.id not in project.type_ids.ids:
                                        project.type_ids = [(4, project_task_type.id)]

                                    _response = {"data": None, "success": True,
                                                 "statusCode": 200,
                                                 "message": "success"}
                    else:
                        _response = {"data": None, "itemsCount": 0, "success": False, "statusCode": 404,
                                     "message": 'project Name Is Required'}

                else:
                    _response = {"data": None, "itemsCount": 0, "success": False, "statusCode": 401,
                                 "message": ' Unauthorized'}
            else:
                _response = {"data": None, "itemsCount": 0, "success": False, "statusCode": 404,
                             "message": "Access Token Is Missing"}
        except Exception as e:
            _response = {"data": None, "itemsCount": 0, "success": False, "statusCode": 400, "message": str(e)}
        finally:
            return json.dumps(_response)
