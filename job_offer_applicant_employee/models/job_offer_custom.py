# -*- coding: utf-8 -*-

# Part of Probuse Consulting Service Pvt Ltd.
# See LICENSE file for full copyright and licensing details.

from odoo import models, fields, api, _

import logging
_logger = logging.getLogger(__name__)

class JobOfferCustomer(models.Model):
    _name = 'job.offer.customer'
    _inherit = ['portal.mixin', 'mail.thread', 'mail.activity.mixin', 'utm.mixin']

    @api.model
    def _get_job_offer_body(self):
        return """
            <p>We are pleased to offer you the [full-time, part-time, etc.] position of [job title] at [company name] 
            with a start date of [start date], contingent upon [background check, I-9 form, etc.]. You will be 
            reporting directly to [manager/supervisor name] at [workplace location]. We believe your skills and 
            experience are an excellent match for our company.</p>
            <br/>
            <p>In this role, you will be required to [briefly mention relevant job duties and responsibilities].</p>
            <br/>
            <p>The annual starting salary for this position is [dollar amount] to be paid on a [monthly, semi-
            monthly, weekly, etc.] basis by [direct deposit, check, etc.], starting on [first pay period]. In 
            addition to this starting salary, we’re offering you [discuss stock options, bonuses, commission 
            structures, etc.].</p>
            <br/>
            <p>Your employment with [company name] will be on an at-will basis, which means you and the company 
            are free to terminate the employment relationship at any time for any reason. This letter is not a 
            contract or guarantee of employment for a definite amount of time.</p>
            <br/>
            <p>As an employee of [company name], you are also eligible for our benefits program, which includes 
            [medical insurance, 401(k), vacation time, etc.], and other benefits which will be described in more 
            detail in the [employee handbook, orientation package, etc.].</p>
            <br/>
            <p>Please confirm your acceptance of this offer by signing and returning this letter by [offer expiration 
            date].</p>
            <br/>
            <p>We are excited to have you join our team! If you have any questions, please feel free to reach out at any time.</p>
            <br/>
            <p>Sincerely,</p>
            <p>[Your Signature]</p>
            <br/>
            <p>[Your Printed Name]</p>
            <p>[Your Job Title]</p>
            <br/>
            <p>Signature: ______________________________</p>
            <p>Printed Name: ___________________________</p>
            <p>Date: __________________________________</p>
       """

    name = fields.Char(
        string="Number",
        default=lambda self: _('New'),
        readonly=True,
        copy= False,
    )
    application_id = fields.Many2one(
        'hr.applicant',
        string="Application",
        domain = "[('emp_id', '!=', False)]",
        required=True
    )
    # employee_id = fields.Many2one(
    #     'hr.employee',
    #     related="application_id.emp_id",
    #     string="Employee",
    #     required=True
    # )
    emp_name = fields.Char(string="Employee Name", required=True)
    offer_date = fields.Date(
        string="Offer Date",
        default= fields.Date.today(),
        required=True
    )
    company_id = fields.Many2one(
        'res.company',
        string="Company",
        required=True
    )
    currency_id = fields.Many2one(
        "res.currency", 
        related='company_id.currency_id', 
        string="Currency", 
        readonly=True, 
        required=True
    )
    note = fields.Html(
        string="Body",
        default = _get_job_offer_body,
    )
    state = fields.Selection([
        ('new', 'New'),
        ('in_progress', 'In Progress'),
        ('given_to_employee', 'Given To Employee'),
        ('done', 'Done'),
        ('cancel', 'Cancel')
        ], 
        string='Status', 
        copy=False, 
        tracking=3,
        default='new',
        index=True,
    )
    monthly_salary = fields.Float(
        string="Monthly Salary",
        required=True
    )
    prepaid_by = fields.Many2one(
        'res.users',
        string="Prepaid By",
        default=lambda self: self.env.user,
        readonly=True
    )
    prepaid_date = fields.Date(
        string='Prepaid Date',
        default= fields.Date.today(),
        readonly=True
    )

    
    @api.onchange('application_id')
    def application_id_change(self):
        for rec in self:
            rec.company_id = rec.application_id.company_id.id

    @api.model
    def create(self, vals):
        vals['name'] = self.env['ir.sequence'].next_by_code('job.offer.customer')
        return super(JobOfferCustomer, self).create(vals)  

    def action_in_progress(self):
        for rec in self:
            rec.state = 'in_progress'

    def action_give_to_employee(self):
        for rec in self:
            rec.state = 'given_to_employee'

    def action_done(self):
        for rec in self:
            rec.state = 'done'

    def action_cancel(self):
        for rec in self:
            rec.state = 'cancel'
