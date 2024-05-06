from odoo.exceptions import UserError

from dateutil import relativedelta

from odoo import models, fields, api, _
from odoo.http import request
from datetime import datetime, date
from collections import defaultdict
import pytz
from odoo.addons.resource.models.resource import datetime_to_string, string_to_datetime, Intervals


class HrContract(models.Model):
    _inherit = 'hr.contract'

    house_allowance = fields.Float('House Allowance', store=True, tracking=True)
    transportation_allowance = fields.Float('Transportation Allowance', store=True, tracking=True)
    other_allowance = fields.Float('Other Allowance', tracking=True)
    other_deduction = fields.Float('Other Deduction')
    over_fifty = fields.Boolean('Employee Over 50')
    over_fifty_amount = fields.Float('Amount')
    gross = fields.Float('Gross', compute='compute_gross', store=True)
    employee_gosi = fields.Boolean(string='Gosi')

    @api.depends('wage', 'house_allowance', 'transportation_allowance')
    def compute_gross(self):
        for rec in self:
            rec.gross = rec.wage + rec.house_allowance + rec.transportation_allowance

    contract_select_rel = fields.Selection(related='employee_id.contract_select')
    emp_statues_rel = fields.Selection(related='employee_id.emp_status')
    contract_statue = fields.Selection(
        string='حالة العقد',
        selection=[('specified', 'محدد'), ('non_specified', 'غير محدد')],
        required=False, )

    contract_status = fields.Selection(
        [('flexible', 'مرن'),
         ('partial', 'جزئ'), ('clearing', 'تمهير'), ('student', 'طالب'), ('intern', 'متدرب'), ('contracted', 'متعاقد'),
         ('distance_working', 'العمل عن بعد'), ('add1', 'شهادة إنجاز'),
         ('un_contracted', 'غير متعاقد'), ('ex_contracted', 'متعاقد خارج قوى')], string='Contract Type')
    # basic_housing = fields.Float('Basic And Hosuing Allowance', compute='compute_basic_housing')
    # basic_transport = fields.Float('Basic And Transportation Allowance', compute='compute_basic_transport')
    social_deductions = fields.Float('Gosi deduction ', compute='compute_social_deductions', store='True')
    social_after_deductions = fields.Float('Net Salary', compute='compute_social_after_deductions')

    num_working_days_month = fields.Integer(default=30,
                                            help="Used as standard rate for overtime calculations regardless "
                                                 "the true working days")
    num_working_hours_day = fields.Integer(default=8,
                                           help="Used as standard rate for overtime calculations regardless "
                                                "the true working hours")
    is_insured = fields.Boolean(string="Is Insured?", default=True, tracking=True)
    fixed_insurance = fields.Float(string="Fixed Insurance Amount", required=False, tracking=True)

    @api.depends('wage', 'transportation_allowance')
    def compute_basic_transport(self):
        for rec in self:
            rec.basic_transport = rec.wage + rec.transportation_allowance

    @api.depends('wage', 'house_allowance')
    def compute_social_deductions(self):
        for rec in self:
            rec.social_deductions = (rec.wage + rec.house_allowance) * .0975
            # total = rec.wage + rec.house_allowance
            # if rec.employee_gosi:
            #     if rec.contract_select_rel == 'saudi':
            #         total_deduct = total * (9.75 / 100)
            #         rec.social_deductions = total_deduct
            #     else:
            #         total_deduct = total * (2 / 100)
            #         rec.social_deductions = total_deduct
            # else:
            #     rec.social_deductions = 0

    @api.depends('wage', 'house_allowance', 'transportation_allowance', 'social_deductions', 'other_allowance')
    def compute_social_after_deductions(self):
        for rec in self:
            if rec.employee_gosi:
                rec.social_after_deductions = (rec.wage + rec.house_allowance + rec.transportation_allowance +
                                               rec.other_allowance) - rec.social_deductions
            else:
                rec.social_after_deductions = 0

            #     if rec.contract_select_rel == 'saudi':
            #         total = rec.wage + rec.house_allowance + rec.transportation_allowance + rec.other_allowance
            #         total_deduct = abs(total - rec.social_deductions)
            #         rec.social_after_deductions = total_deduct
            #     else:
            #         total = rec.wage + rec.house_allowance + rec.transportation_allowance + rec.other_allowance
            #         rec.social_after_deductions = total
            # else:
            #     rec.social_after_deductions = 0

    @api.depends('wage', 'house_allowance')
    def compute_basic_housing(self):
        for rec in self:
            rec.basic_housing = rec.wage + rec.house_allowance

    # def insurance_total_alw_basic(self):
    #     emp = self.env['hr.payroll.structure'].search([('active', '=', True)])
    #     emp_code = emp.rule_ids.filtered(lambda l: l.code == 'EISR')
    #     total_list = []
    #     for rec in emp.rule_ids:
    #         if rec.sequence <= emp_code.sequence and rec.category_id.code in ['BASIC', 'ALW']:
    #             total_list.append(rec.sequence)
    #     return total_list

    def company_insurance_salary(self, categories):
        house_basic = categories.BASIC + categories.ALW
        if self.contract_select_rel == 'saudi':
            if self.over_fifty == True:
                total_over_fifty = abs(house_basic - self.over_fifty_amount)
                total = total_over_fifty * (11.75 / 100)
            else:
                total = house_basic * (11.75 / 100)
            return -1 * total
        elif self.contract_select_rel == 'non_saudi':
            if self.over_fifty == True:
                total_over_fifty = abs(house_basic - self.over_fifty_amount)
                total = total_over_fifty * (2 / 100)
            else:
                total = house_basic * (2 / 100)
            return -1 * total
        else:
            return 0

    def employee_insurance_salary(self, categories):
        house_basic = categories.BASIC + categories.ALW
        if self.contract_select_rel == 'saudi':
            if self.over_fifty == True:
                total_over_fifty = abs(house_basic - self.over_fifty_amount)
                total = total_over_fifty * (9.75 / 100)
            else:
                total = house_basic * (9.75 / 100)
            return -1 * total
        elif self.contract_select_rel == 'non_saudi':
            return 0
        else:
            return 0

    def contract_end_date_notify(self):
        contracts = self.sudo().search([('state', '=', 'open')])
        users = self.env['res.users'].search([])
        for contract in contracts:
            if contract.date_end:
                delta = relativedelta.relativedelta(contract.date_end, date.today())
                if delta.months == 2 and delta.days == 15 and delta.years == 0:
                    for user in users:
                        notification_ids = [(0, 0, {
                            'res_partner_id': user.partner_id.id,
                            'notification_type': 'inbox'
                        })]
                        action_id = self.env.ref('hr_contract.action_hr_contract')  # action id
                        base_url = request.env['ir.config_parameter'].sudo().get_param('web.base.url')
                        base_url += '/web#id=%d&amp;view_type=form&amp;model=%s' % (contract.id, self._name)
                        base_url += '&amp;action=%d' % (action_id.id)
                        contract.message_post(record_name='Contract End Date',
                                              body=""" Contract Will End In 75 Days """ + ' ' +
                                                   """<br> You can access contract details from here: <br>"""
                                                   + """<a href="%s">Link</a>""" % (
                                                       base_url)
                                              , message_type="notification",
                                              subtype_xmlid="mail.mt_comment",
                                              author_id=user.partner_id.id,
                                              notification_ids=notification_ids,
                                              )

    @api.constrains('state')
    def constrain_state(self):
        employee_contracts = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')])
        if len(employee_contracts) > 1:
            error_message = "Multiple running contracts for employee: " + str(self.employee_id.name)
            raise UserError(error_message)

    def _get_contract_work_entries_values(self, date_start, date_stop):
        contract_vals = []
        bypassing_work_entry_type_codes = self._get_bypassing_work_entry_type_codes()
        for contract in self:
            employee = contract.employee_id
            calendar = contract.resource_calendar_id
            resource = employee.resource_id
            tz = pytz.timezone(calendar.tz)
            start_dt = pytz.utc.localize(date_start) if not date_start.tzinfo else date_start
            end_dt = pytz.utc.localize(date_stop) if not date_stop.tzinfo else date_stop

            attendances = calendar._attendance_intervals_batch(
                start_dt, end_dt, resources=resource, tz=tz
            )[resource.id]

            # Other calendars: In case the employee has declared time off in another calendar
            # Example: Take a time off, then a credit time.
            # YTI TODO: This mimics the behavior of _leave_intervals_batch, while waiting to be cleaned
            # in master.
            resources_list = [self.env['resource.resource'], resource]
            resource_ids = [False, resource.id]
            leave_domain = contract._get_leave_domain(start_dt, end_dt)
            result = defaultdict(lambda: [])
            tz_dates = {}
            for leave in self.env['resource.calendar.leaves'].sudo().search(leave_domain):
                for resource in resources_list:
                    if leave.resource_id.id not in [False, resource.id]:
                        continue
                    tz = tz if tz else pytz.timezone((resource or contract).tz)
                    if (tz, start_dt) in tz_dates:
                        start = tz_dates[(tz, start_dt)]
                    else:
                        start = start_dt.astimezone(tz)
                        tz_dates[(tz, start_dt)] = start
                    if (tz, end_dt) in tz_dates:
                        end = tz_dates[(tz, end_dt)]
                    else:
                        end = end_dt.astimezone(tz)
                        tz_dates[(tz, end_dt)] = end
                    dt0 = string_to_datetime(leave.date_from).astimezone(tz)
                    dt1 = string_to_datetime(leave.date_to).astimezone(tz)
                    result[resource.id].append((max(start, dt0), min(end, dt1), leave))
            mapped_leaves = {r.id: Intervals(result[r.id]) for r in resources_list}
            leaves = mapped_leaves[resource.id]

            real_attendances = attendances - leaves
            real_leaves = attendances - real_attendances

            # A leave period can be linked to several resource.calendar.leave
            split_leaves = []
            for leave_interval in leaves:
                if leave_interval[2] and len(leave_interval[2]) > 1:
                    split_leaves += [(leave_interval[0], leave_interval[1], l) for l in leave_interval[2]]
                else:
                    split_leaves += [(leave_interval[0], leave_interval[1], leave_interval[2])]
            leaves = split_leaves

            # Attendances
            default_work_entry_type = contract._get_default_work_entry_type()
            for interval in real_attendances:
                work_entry_type_id = interval[2].mapped('work_entry_type_id')[:1] or default_work_entry_type
                # All benefits generated here are using datetimes converted from the employee's timezone
                contract_vals += [{
                    'name': "%s: %s" % (work_entry_type_id.name, employee.name),
                    'date_start': interval[0].astimezone(pytz.utc).replace(tzinfo=None),
                    'date_stop': interval[1].astimezone(pytz.utc).replace(tzinfo=None),
                    'work_entry_type_id': work_entry_type_id.id,
                    'employee_id': employee.id,
                    'contract_id': contract.id,
                    'company_id': contract.company_id.id,
                    'state': 'draft',
                }]

            for interval in real_leaves:
                # Could happen when a leave is configured on the interface on a day for which the
                # employee is not supposed to work, i.e. no attendance_ids on the calendar.
                # In that case, do try to generate an empty work entry, as this would raise a
                # sql constraint error
                if interval[0] == interval[1]:  # if start == stop
                    continue
                leave_entry_type = contract._get_interval_leave_work_entry_type(interval, leaves,
                                                                                bypassing_work_entry_type_codes)
                interval_start = interval[0].astimezone(pytz.utc).replace(tzinfo=None)
                interval_stop = interval[1].astimezone(pytz.utc).replace(tzinfo=None)
                contract_vals += [dict([
                                           ('name', "%s%s" % (
                                               leave_entry_type.name + ": " if leave_entry_type else "",
                                               employee.name)),
                                           ('date_start', interval_start),
                                           ('date_stop', interval_stop),
                                           ('work_entry_type_id', leave_entry_type.id),
                                           ('employee_id', employee.id),
                                           ('company_id', contract.company_id.id),
                                           ('state', 'draft'),
                                           ('contract_id', contract.id),
                                       ] + contract._get_more_vals_leave_interval(interval, leaves))]
        return contract_vals

    def _get_work_entries_values(self, date_start, date_stop):
        """
        Generate a work_entries list between date_start and date_stop for one contract.
        :return: list of dictionnary.
        """
        contract_vals = self._get_contract_work_entries_values(date_start, date_stop)

        for contract in self:
            # If we generate work_entries which exceeds date_start or date_stop, we change boundaries on contract
            if contract_vals:
                # Handle empty work entries for certain contracts, could happen on an attendance based contract
                # NOTE: this does not handle date_stop or date_start not being present in vals
                dates_stop = [x['date_stop'] for x in contract_vals if x['contract_id'] == contract.id]
                if dates_stop:
                    date_stop_max = max(dates_stop)
                    if date_stop_max > contract.date_generated_to:
                        contract.date_generated_to = date_stop_max

                dates_start = [x['date_start'] for x in contract_vals if x['contract_id'] == contract.id]
                if dates_start:
                    date_start_min = min(dates_start)
                    if date_start_min < contract.date_generated_from:
                        contract.date_generated_from = date_start_min

        return contract_vals

    def _generate_work_entries(self, date_start, date_stop, force=False):
        canceled_contracts = self.filtered(lambda c: c.state == 'cancel')
        if canceled_contracts:
            raise UserError(
                _("Sorry, generating work entries from cancelled contracts is not allowed.") + '\n%s' % (
                    ', '.join(canceled_contracts.mapped('name'))))
        # vals_list = []
        # date_start = fields.Datetime.to_datetime(date_start)
        # date_stop = datetime.combine(fields.Datetime.to_datetime(date_stop), datetime.max.time())
        #
        # intervals_to_generate = defaultdict(lambda: self.env['hr.contract'])
        # for contract in self:
        #     contract_start = fields.Datetime.to_datetime(contract.date_start)
        #     contract_stop = datetime.combine(fields.Datetime.to_datetime(contract.date_end or datetime.max.date()),
        #                                      datetime.max.time())
        #     date_start_work_entries = max(date_start, contract_start)
        #     date_stop_work_entries = min(date_stop, contract_stop)
        #     if force:
        #         intervals_to_generate[(date_start_work_entries, date_stop_work_entries)] |= contract
        #         continue
        #
        #     # In case the date_generated_from == date_generated_to, move it to the date_start to
        #     # avoid trying to generate several months/years of history for old contracts for which
        #     # we've never generated the work entries.
        #     if contract.date_generated_from == contract.date_generated_to:
        #         contract.write({
        #             'date_generated_from': date_start,
        #             'date_generated_to': date_start,
        #         })
        #     # For each contract, we found each interval we must generate
        #     last_generated_from = min(contract.date_generated_from, contract_stop)
        #     if last_generated_from > date_start_work_entries:
        #         contract.date_generated_from = date_start_work_entries
        #         intervals_to_generate[(date_start_work_entries, last_generated_from)] |= contract
        #
        #     last_generated_to = max(contract.date_generated_to, contract_start)
        #     if last_generated_to < date_stop_work_entries:
        #         contract.date_generated_to = date_stop_work_entries
        #         intervals_to_generate[(last_generated_to, date_stop_work_entries)] |= contract
        #
        # for interval, contracts in intervals_to_generate.items():
        #     date_from, date_to = interval
        #     vals_list.extend(contracts._get_work_entries_values(date_from, date_to))
        #
        # if not vals_list:
        #     return self.env['hr.work.entry']
        #
        # return self.env['hr.work.entry'].create(vals_list)

    # @api.onchange('wage')
    # def _compute_house_allowance(self):
    #     self.house_allowance = .25 * self.wage
    #
    # @api.onchange('wage')
    # def _compute_transportation_allowance(self):
    #     self.transportation_allowance = .1 * self.wage
