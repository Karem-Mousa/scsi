from odoo import fields, api, models, _
from odoo import exceptions

from datetime import datetime, time

from dateutil import rrule
import base64

from datetime import date, datetime
from dateutil.relativedelta import relativedelta

from odoo.addons.hr_payroll.models.browsable_object import BrowsableObject, InputLine, WorkedDays, Payslips
from odoo.exceptions import UserError, ValidationError
from collections import defaultdict
from markupsafe import Markup

from odoo import api, fields, models, _
from odoo.tools import float_compare, float_is_zero, plaintext2html


class HrPayslipInput(models.Model):
    _inherit = 'hr.payslip.input'

    input_type_id = fields.Many2one('hr.payslip.input.type', string='Type', required=False,
                                    domain="['|', ('id', 'in', _allowed_input_type_ids), ('struct_ids', '=', False)]")


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    basic_wage = fields.Monetary(compute='_compute_basic_net', store=False)
    net_wage = fields.Monetary(compute='_compute_basic_net', store=False)
    gross_wage = fields.Monetary(compute='_compute_gross', store=False)

    identification_id_rel = fields.Char(related='employee_id.identification_id')
    attendance_id_char_rel = fields.Char(related='employee_id.attendance_id_char')

    def _compute_gross(self):
        line_values = (self._origin)._get_line_values(['GROSS'])
        for payslip in self:
            payslip.gross_wage = line_values['GROSS'][payslip._origin.id]['total']

    # def _prepare_line_values(self, line, account_id, date, debit, credit):
    #     account = self.env['account.account'].browse(account_id)
    #     if account.user_type_id.is_expense_or_cost_revenue == True:
    #         return {
    #             'name': line.name,
    #             'partner_id': line.partner_id.id,
    #             'account_id': account_id,
    #             'journal_id': line.slip_id.struct_id.journal_id.id,
    #             'date': date,
    #             'debit': debit,
    #             'credit': credit,
    #             'analytic_account_id': line.slip_id.employee_id.branch.analytic_account_id.id
    #         }
    #     else:
    #         return {
    #             'name': line.name,
    #             'partner_id': line.partner_id.id,
    #             'account_id': account_id,
    #             'journal_id': line.slip_id.struct_id.journal_id.id,
    #             'date': date,
    #             'debit': debit,
    #             'credit': credit,
    #             'analytic_account_id': False
    #         }
    #
    # def _get_existing_lines(self, line_ids, line, account_id, debit, credit):
    #     account = self.env['account.account'].browse(account_id)
    #     if account.user_type_id.is_expense_or_cost_revenue == True:
    #         line_analytic_account_id = line.slip_id.employee_id.branch.analytic_account_id.id
    #         existing_lines = (
    #             line_id for line_id in line_ids if
    #             line_id['name'] == line.name
    #             and line_id['account_id'] == account_id
    #             and line_id['analytic_account_id'] == line_analytic_account_id
    #             and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0)))
    #     else:
    #         existing_lines = (
    #             line_id for line_id in line_ids if
    #             line_id['name'] == line.name
    #             and line_id['account_id'] == account_id
    #             and ((line_id['debit'] > 0 and credit <= 0) or (line_id['credit'] > 0 and debit <= 0)))
    #
    #     return next(existing_lines, False)
    #
    #
    # def _action_create_account_move(self):
    #     precision = self.env['decimal.precision'].precision_get('Payroll')
    #
    #     # Add payslip without run
    #     payslips_to_post = self.filtered(lambda slip: not slip.payslip_run_id)
    #
    #     # Adding pay slips from a batch and deleting pay slips with a batch that is not ready for validation.
    #     payslip_runs = (self - payslips_to_post).mapped('payslip_run_id')
    #     for run in payslip_runs:
    #         if run._are_payslips_ready():
    #             payslips_to_post |= run.slip_ids
    #
    #     # A payslip need to have a done state and not an accounting move.
    #     payslips_to_post = payslips_to_post.filtered(lambda slip: slip.state == 'done' and not slip.move_id)
    #
    #     # Check that a journal exists on all the structures
    #     if any(not payslip.struct_id for payslip in payslips_to_post):
    #         raise ValidationError(_('One of the contract for these payslips has no structure type.'))
    #     if any(not structure.journal_id for structure in payslips_to_post.mapped('struct_id')):
    #         raise ValidationError(_('One of the payroll structures has no account journal defined on it.'))
    #
    #     # Map all payslips by structure journal and pay slips month.
    #     # {'journal_id': {'month': [slip_ids]}}
    #     slip_mapped_data = defaultdict(lambda: defaultdict(lambda: self.env['hr.payslip']))
    #     for slip in payslips_to_post:
    #         slip_mapped_data[slip.struct_id.journal_id.id][fields.Date().end_of(slip.date_to, 'month')] |= slip
    #     for journal_id in slip_mapped_data: # For each journal_id.
    #         for slip_date in slip_mapped_data[journal_id]: # For each month.
    #             line_ids = []
    #             debit_sum = 0.0
    #             credit_sum = 0.0
    #             date = slip_date
    #             move_dict = {
    #                 'narration': '',
    #                 'ref': date.strftime('%B %Y'),
    #                 'journal_id': journal_id,
    #                 'date': date,
    #             }
    #
    #             for slip in slip_mapped_data[journal_id][slip_date]:
    #                 move_dict['narration'] += plaintext2html(slip.number or '' + ' - ' + slip.employee_id.name or '')
    #                 move_dict['narration'] += Markup('<br/>')
    #                 for line in slip.line_ids.filtered(lambda line: line.category_id and line.salary_rule_id.is_analytic):
    #                     amount = line.total
    #                     if line.code == 'NET': # Check if the line is the 'Net Salary'.
    #                         for tmp_line in slip.line_ids.filtered(lambda line: line.category_id and line.salary_rule_id.is_analytic):
    #                             if tmp_line.salary_rule_id.not_computed_in_net: # Check if the rule must be computed in the 'Net Salary' or not.
    #                                 if amount > 0:
    #                                     amount -= abs(tmp_line.total)
    #                                 elif amount < 0:
    #                                     amount += abs(tmp_line.total)
    #                     if float_is_zero(amount, precision_digits=precision):
    #                         continue
    #                     debit_account_id = line.salary_rule_id.account_debit.id
    #                     credit_account_id = line.salary_rule_id.account_credit.id
    #
    #                     if debit_account_id: # If the rule has a debit account.
    #                         debit = amount if amount > 0.0 else 0.0
    #                         credit = -amount if amount < 0.0 else 0.0
    #
    #                         debit_line = self._get_existing_lines(
    #                             line_ids, line, debit_account_id, debit, credit)
    #
    #                         if not debit_line:
    #                             debit_line = self._prepare_line_values(line, debit_account_id, date, debit, credit)
    #                             line_ids.append(debit_line)
    #                         else:
    #                             debit_line['debit'] += debit
    #                             debit_line['credit'] += credit
    #
    #                     if credit_account_id: # If the rule has a credit account.
    #                         debit = -amount if amount < 0.0 else 0.0
    #                         credit = amount if amount > 0.0 else 0.0
    #                         credit_line = self._get_existing_lines(
    #                             line_ids, line, credit_account_id, debit, credit)
    #
    #                         if not credit_line:
    #                             credit_line = self._prepare_line_values(line, credit_account_id, date, debit, credit)
    #                             line_ids.append(credit_line)
    #                         else:
    #                             credit_line['debit'] += debit
    #                             credit_line['credit'] += credit
    #
    #             for line_id in line_ids: # Get the debit and credit sum.
    #                 debit_sum += line_id['debit']
    #                 credit_sum += line_id['credit']
    #
    #             # The code below is called if there is an error in the balance between credit and debit sum.
    #             acc_id = slip.sudo().journal_id.default_account_id.id
    #             if float_compare(credit_sum, debit_sum, precision_digits=precision) == -1:
    #                 if not acc_id:
    #                     raise UserError(_('The Expense Journal "%s" has not properly configured the Credit Account!') % (slip.journal_id.name))
    #                 existing_adjustment_line = (
    #                     line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
    #                 )
    #                 adjust_credit = next(existing_adjustment_line, False)
    #
    #                 if not adjust_credit:
    #                     adjust_credit = {
    #                         'name': _('Adjustment Entry'),
    #                         'partner_id': False,
    #                         'account_id': acc_id,
    #                         'journal_id': slip.journal_id.id,
    #                         'date': date,
    #                         'debit': 0.0,
    #                         'credit': debit_sum - credit_sum,
    #                     }
    #                     line_ids.append(adjust_credit)
    #                 else:
    #                     adjust_credit['credit'] = debit_sum - credit_sum
    #
    #             elif float_compare(debit_sum, credit_sum, precision_digits=precision) == -1:
    #                 if not acc_id:
    #                     raise UserError(_('The Expense Journal "%s" has not properly configured the Debit Account!') % (slip.journal_id.name))
    #                 existing_adjustment_line = (
    #                     line_id for line_id in line_ids if line_id['name'] == _('Adjustment Entry')
    #                 )
    #                 adjust_debit = next(existing_adjustment_line, False)
    #
    #                 if not adjust_debit:
    #                     adjust_debit = {
    #                         'name': _('Adjustment Entry'),
    #                         'partner_id': False,
    #                         'account_id': acc_id,
    #                         'journal_id': slip.journal_id.id,
    #                         'date': date,
    #                         'debit': credit_sum - debit_sum,
    #                         'credit': 0.0,
    #                     }
    #                     line_ids.append(adjust_debit)
    #                 else:
    #                     adjust_debit['debit'] = credit_sum - debit_sum
    #
    #             # Add accounting lines in the move
    #             move_dict['line_ids'] = [(0, 0, line_vals) for line_vals in line_ids]
    #             move = self.env['account.move'].sudo().create(move_dict)
    #             for slip in slip_mapped_data[journal_id][slip_date]:
    #                 slip.write({'move_id': move.id, 'date': date})
    #     return True

    def _get_payslip_lines(self):
        def _sum_salary_rule_category(localdict, category, amount):
            if category.parent_id:
                localdict = _sum_salary_rule_category(localdict, category.parent_id, amount)
            localdict['categories'].dict[category.code] = localdict['categories'].dict.get(category.code, 0) + amount
            return localdict

        self.ensure_one()
        result = {}
        rules_dict = {}
        worked_days_dict = {line.code: line for line in self.worked_days_line_ids if line.code}
        inputs_dict = {line.code: line for line in self.input_line_ids if line.code}

        employee = self.employee_id
        contract = self.contract_id
        payslip = self.env['hr.payslip'].browse(self.id)

        localdict = {
            **self._get_base_local_dict(),
            **{
                'categories': BrowsableObject(employee.id, {}, self.env),
                'rules': BrowsableObject(employee.id, rules_dict, self.env),
                'payslip': Payslips(employee.id, self, self.env),
                'worked_days': WorkedDays(employee.id, worked_days_dict, self.env),
                'inputs': InputLine(employee.id, inputs_dict, self.env),
                'employee': employee,
                'contract': contract
            }
        }
        for rule in sorted(self.struct_id.rule_ids, key=lambda x: x.sequence):
            localdict.update({
                'result': None,
                'result_qty': 1.0,
                'result_rate': 100})
            # Modification here
            if rule.contract_valid_based:
                contract_rate = contract.get_work_ratio(payslip.date_from, payslip.date_to)
                localdict['result_rate'] = 100.0 * contract_rate
            # end modification
            if rule._satisfy_condition(localdict):
                amount, qty, rate = rule._compute_rule(localdict)
                # check if there is already a rule computed with that code
                previous_amount = rule.code in localdict and localdict[rule.code] or 0.0
                # set/overwrite the amount computed for this rule in the localdict
                tot_rule = amount * qty * rate / 100.0
                localdict[rule.code] = tot_rule
                rules_dict[rule.code] = rule
                # sum the amount for its salary category
                localdict = _sum_salary_rule_category(localdict, rule.category_id, tot_rule - previous_amount)
                # create/overwrite the rule in the temporary results
                result[rule.code] = {
                    'sequence': rule.sequence,
                    'code': rule.code,
                    'name': rule.name,
                    'note': rule.note,
                    'salary_rule_id': rule.id,
                    'contract_id': contract.id,
                    'employee_id': employee.id,
                    'amount': amount,
                    'quantity': qty,
                    'rate': rate,
                    'slip_id': self.id,
                }
        return result.values()