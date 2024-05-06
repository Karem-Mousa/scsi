from odoo import fields, models, api, _

import pytz
from dateutil.relativedelta import relativedelta


class HrEmployee(models.Model):
    _inherit = "hr.employee"

    hours_this_month = fields.Float(
        compute='_compute_hours_last_month', groups="hr_attendance.group_hr_attendance_user")
    hours_this_month_display = fields.Char(
        compute='_compute_hours_this_month', groups="hr_attendance.group_hr_attendance_user")

    def _compute_hours_this_month(self):
        now = fields.Datetime.now()
        now_utc = pytz.utc.localize(now)
        for employee in self:
            tz = pytz.timezone(employee.tz or 'UTC')
            now_tz = now_utc.astimezone(tz)
            start_tz = now_tz + relativedelta(day=1, hour=0, minute=0, second=0, microsecond=0)
            start_naive = start_tz.astimezone(pytz.utc).replace(tzinfo=None)
            end_tz = now_tz + relativedelta(hour=0, minute=0, second=0, microsecond=0)
            end_naive = end_tz.astimezone(pytz.utc).replace(tzinfo=None)

            attendances = self.env['hr.attendance'].search([
                ('employee_id', '=', employee.id),
                '&',
                ('check_in', '<=', end_naive),
                ('check_out', '>=', start_naive),
            ])

            hours = 0
            for attendance in attendances:
                check_in = max(attendance.check_in, start_naive)
                check_out = min(attendance.check_out, end_naive)
                hours += (check_out - check_in).total_seconds() / 3600.0

            employee.hours_this_month = round(hours, 2)
            employee.hours_this_month_display = "%g" % employee.hours_this_month

    @api.model
    def name_search(self, name, args=None, operator='ilike', limit=100):
        args = args or []
        recs = self.search([('identification_id', operator, name)] + args, limit=limit)
        if not recs.ids:
            return super(HrEmployee, self).name_search(name=name, args=args,
                                                       operator=operator,
                                                       limit=limit)
        return recs.name_get()

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        res.attendance_id_char = self.env['ir.sequence'].next_by_code(
                'hr.employee')
        return res





