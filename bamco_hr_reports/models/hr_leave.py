from odoo.exceptions import ValidationError

from dateutil import relativedelta

from odoo import models, fields, api, _
from odoo.http import request
from datetime import datetime, date, timedelta
from collections import defaultdict
import pytz
from odoo.addons.resource.models.resource import datetime_to_string, string_to_datetime, Intervals


class HrLeave(models.Model):
    _inherit = 'hr.leave'

    code = fields.Char('Code')
    alt_employee_id = fields.Many2one('hr.employee', 'Alternative Employee')
    return_from_leave = fields.Date(compute='compute_return_from_leave', store=True)

    @api.depends('request_date_to')
    def compute_return_from_leave(self):
        for rec in self:
            if rec.request_date_to:
                request_to = rec.request_date_to + timedelta(days=1)
                request_day = request_to.strftime("%A")
                # work_sechdule = self.env['resource.calendar.attendance'].search(
                #     [('calendar_id', '=', rec.employee_id.contract_id.resource_calendar_id.id)])
                request_to_date = request_to
                for work in rec.employee_id.contract_id.resource_calendar_id.attendance_ids:
                    if work.dayofweek == request_day:
                        request_to_date += timedelta(days=1)
                    else:
                        request_to_date = request_to
                rec.return_from_leave = request_to_date

    def unlink(self):
        res = super(HrLeave, self).unlink()
        leaves = self.env['hr.leave'].search([])
        seq = 0
        for leave in leaves:
            seq += 1
            leave.code = str(seq)
        sequen = seq + 1
        self.code = str(sequen)
        return res

    @api.model
    def create(self, vals):
        leaves = self.env['hr.leave'].search([])
        seq = 0
        for leave in leaves:
            seq += 1
            leave.code = str(seq)
        sequen = seq + 1
        vals['code'] = str(sequen)
        res = super(HrLeave, self).create(vals)
        return res

    def generate_qweb_report(self):
        return self.env.ref('bamco_hr_reports.bamco_hr_leave').sudo().report_action(docids=self.ids)
