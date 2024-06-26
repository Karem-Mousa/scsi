# -*- coding: utf-8 -*-
import math
from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError
from dateutil.relativedelta import relativedelta
from datetime import datetime


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread', 'mail.activity.mixin']

    @api.constrains('requested_amount')
    def _requested_so(self):
        if self.requested_amount and self.remaining_budget:
            if self.requested_amount < 0:
                raise UserError(_('The Requested Amount Must Be Larger Than Zero.'))
            if self.requested_amount > self.remaining_budget:
                raise UserError(_('The Requested Amount Must Be Larger Or Equal Than Remaining Budget.'))
        elif not self.requested_amount:
            raise UserError(_('The Requested Amount Is Required.'))

        elif not self.remaining_budget:
            raise UserError(_('The Remaining Budget IS Required.'))

        return True


    def unlink(self):
        if self.state != 'draft':
            raise ValidationError(_('Error ! You Cannot Delete The Loan Tn This State '))
        else:
            for line in self.loan_line:
                if line.state == 'unpaid':
                    line.unlink()
                else:
                    raise ValidationError(_('Error ! You Have Line Piad You Cannot Delete The Loan .'))
        return super(HrLoan, self).unlink()


    @api.depends('employee_id', 'loan_type', 'requested_date')
    def compute_remaining_budget(self):
        remaining_budget = 0
        loan_line_obj = self.env['hr.loan.line']

        contract_id = self.env['hr.contract'].search(
            [('employee_id', '=', self.employee_id.id), ('state', '=', 'open')],
            order='date_start desc', limit=1)
        if self.employee_id and self.loan_type == 'short_term':
            total_unpaid_amount = 0
            loan_line_data = loan_line_obj.search(
                [('loan_id.employee_id', '=', self.employee_id.id), ('state', 'in', ('unpaid', 'partial_paid')),
                 ('loan_type', '=', 'short_term')])
            for loan_line in loan_line_data:
                total_unpaid_amount += loan_line.amount - loan_line.paid_amount

            if contract_id:
                total_loan_budget = contract_id.total_loan_budget
                if total_unpaid_amount <= total_loan_budget:
                    remaining_budget = total_loan_budget - total_unpaid_amount
                else:
                    remaining_budget = 0

        elif self.employee_id and self.loan_type == 'long_term':
            total_unpaid_amount = 0
            loan_line_data = loan_line_obj.search(
                [('loan_id.employee_id', '=', self.employee_id.id), ('state', 'in', ('unpaid', 'partial_paid')),
                 ('loan_type', '=', 'long_term')])
            for loan_line in loan_line_data:
                total_unpaid_amount += loan_line.amount - loan_line.paid_amount

            if contract_id:
                total_long_term_loan_budget = contract_id.total_long_term_loan_budget
                if total_unpaid_amount <= total_long_term_loan_budget:
                    remaining_budget = total_long_term_loan_budget - total_unpaid_amount
                else:
                    remaining_budget = 0

        self.remaining_budget = remaining_budget

    name = fields.Char(required=True,track_visibility='always')
    loan_type = fields.Selection(string="Loan Type",
                                 selection=[('long_term', 'Loan Long Term'),
                                            ('short_term', 'Loan Short Term')],
                                 required=True,track_visibility='always')

    debit_advance_balance = fields.Integer(
        string='رصيد السلف المدين',
        required=False)

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        self.debit_advance_balance = self.employee_id.total_unpaid_loan

    remaining_budget = fields.Float(string="Total Loan Budget", compute=compute_remaining_budget, store=True,
                                    required=False, )
    employee_id = fields.Many2one('hr.employee', string='Employee', required=True,)
    company_id = fields.Many2one(related='employee_id.company_id', string='Company', readonly=True, store=True)
    requested_date = fields.Date(default=fields.Date.today(),track_visibility='always')
    settlement_date = fields.Date(string='Start Date For Settlement', default=fields.Date.today())
    requested_amount = fields.Float(required=True)
    installment_amount = fields.Float(required=True)
    state = fields.Selection(
        [('draft', 'Draft'), ('cancel', 'Cancelled'),
         ('approved', 'Approved'), ('sent', 'Sent'), ('closed', 'Closed')],
        default='draft',
        readonly=True,
        copy=False,
        track_visibility='onchange')

    loan_line = fields.One2many('hr.loan.line', 'loan_id')
    journal_created = fields.Boolean(default=False)
    total_unpaid = fields.Float(compute='_compute_total_unpaid', store=True)
    identification_id_rel = fields.Char(related='employee_id.identification_id')
    attendance_id_char_rel = fields.Char(related='employee_id.attendance_id_char')


    @api.depends('loan_line')
    def _compute_total_unpaid(self):
        self.total_unpaid = 0
        for line in self.loan_line:
            self.total_unpaid += (line.amount - line.paid_amount)


    @api.constrains('requested_amount')
    def _requested_so(self):
        if not self.requested_amount:
            raise UserError(_('The Requested Amount Is Required.'))

        return True


    def unlink(self):
        if self.state != 'draft':
            raise ValidationError(_('Error ! You Cannot Delete The Loan Tn This State '))
        else:
            for line in self.loan_line:
                if line.state == 'unpaid':
                    line.unlink()
                else:
                    raise ValidationError(_('Error ! You Have Line Piad You Cannot Delete The Loan .'))
        return super(HrLoan, self).unlink()


    def action_approved(self):
        """ Put the state of the Loan into approved state """
        if self.loan_line:
            requested_amount = self.requested_amount

            total_amount = sum((one_line.amount - one_line.paid_amount) for one_line in self.loan_line)
            if round(total_amount,2) != requested_amount:
                raise ValidationError(_('Error ! Total Amount In lines Must Be Equal The Requested Amount.'))
            self.write({'state': 'approved'})
        else:
            raise ValidationError(_('Error ! You Cannot Approved Without Lines .'))
        return True


    def action_cancel(self):
        """ Put the state of the Loan into cancel state """
        if self.state == 'draft':
            self.write({'state': 'cancel'})
        else:
            raise ValidationError(_('Error ! You Cannot Cancel Loan In Approved State .'))
        return True


    @api.depends('settlement_date', 'requested_amount', 'installment_amount')
    def action_populate(self):
        if self.installment_amount:
            loan_line = self.env['hr.loan.line']
            if self.loan_line:
                for line in self.loan_line:
                    line.unlink()
            requested_amount = self.requested_amount

            amount = self.installment_amount
            installment = int(math.floor(self.requested_amount / amount))
            tagme3a = round(amount, 2) * float(installment)
            diff_nesba = 0
            if requested_amount != tagme3a:
                diff_nesba = requested_amount - tagme3a
            if diff_nesba < 0:
                raise ValidationError(_('Total of installments is greater than the requested amount'))

            date_start_dt = fields.Datetime.from_string(self.settlement_date)
            for i in range(installment):
                # add_diff = 0.0
                # if i == 0:
                #     add_diff = diff_nesba
                loan_line.create(
                    {'amount': round(amount, 2) , 'date': date_start_dt.date(), 'loan_id': self.id,
                     'state': 'unpaid'})
                date_start_dt = (date_start_dt + relativedelta(months=+1))
            if diff_nesba > 0:
                loan_line.create(
                    {'amount': diff_nesba, 'date': date_start_dt.date(), 'loan_id': self.id,
                     'state': 'unpaid'})
        else:
            raise ValidationError(_('Error ! Number Of Months Must Be Larger Than Zero .'))
        return True

    ##

    def send_payment_request(self):
        
        if self.employee_id.address_home_id:
            # if self.employee_id.address_home_id.customer == True:
            if 1 == 1:
                request_date = fields.Date.today()

                vals = {
                        'desc': self.name,
                        'req_amount': self.requested_amount,
                        'req_date': request_date,
                        'employee_id': self.employee_id.id,
                        'partner_id': self.employee_id.address_home_id.id,
                        'loan_line_ids': [(0, 0, {'date': l.date,'amount': l.amount,}) for l in self.loan_line]

                        }
                loan_pay_obj = self.env['loan.payment'].create(vals)
                loan_pay_obj.partner_type = 'customer'
                self.state = 'sent'

                return {
                                'name': 'Message',
                                'type': 'ir.actions.act_window',
                                'view_type': 'form',
                                'view_mode': 'form',
                                'res_model': 'acc.loan.payment.view.wizard',
                                'target': 'new',
                                'context': {'default_name': "Payment Loan Request Sent Successfully."}
                                }
            else:
                raise ValidationError('Related Partner of Employee is not a Customer')

        else:
            raise ValidationError('Employee does not has Related Partner')

class HrLoanLine(models.Model):
    _name = 'hr.loan.line'

    date = fields.Date()
    amount = fields.Float(string='')
    paid_amount = fields.Float(string='Paid Amount')
    loan_id = fields.Many2one('hr.loan', string='Loan Reference', readonly=True)
    payslip_id = fields.Many2one('hr.payslip', string='Payslip', )
    state = fields.Selection([('unpaid', 'Un Paid'), ('partial_paid', 'Partially Paid'), ('paid', 'Paid')],
                             default='unpaid',
                             readonly=False,
                             copy=False)
    loan_type = fields.Selection(string="Loan Type",
                                 selection=[('long_term', 'Loan Long Term'),
                                            ('short_term', 'Loan Short Term')],
                                 related='loan_id.loan_type', store=True)

    def accounting_register(self, installment=0):
        if self.loan_id.employee_id.address_home_id and installment:
            # if self.loan_id.employee_id.address_home_id.customer == True:
            if 1 == 1:
                request_date = fields.Date.today()
                vals = {
                    # 'name': self.env['ir.sequence'].next_by_code('loan.payment'),
                    'desc': self.loan_id.name,
                    'req_amount': installment,
                    'req_date': request_date,
                    'employee_id': self.loan_id.employee_id.id,
                    'partner_id': self.loan_id.employee_id.address_home_id.id,
                    'loan_installment_date': self.date
                }
                loan_pay_obj = self.env['loan.payment'].create(vals)

                loan_pay_obj.partner_type = 'customer'
            else:
                raise ValidationError('Related Partner of Employee is not a Customer')

        else:
            raise ValidationError('Employee does not has Related Partner')


class AccLoanPaymentViewWizard(models.TransientModel):
    _name = 'acc.loan.payment.view.wizard'
