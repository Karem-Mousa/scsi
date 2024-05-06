# -*- coding: utf-8 -*-

from odoo import api, fields, models, _

class JobOfferCreateWizard(models.TransientModel):
    _name = "job.offer.create.wizard"

    @api.model
    def default_get(self, fields):
        res = super(JobOfferCreateWizard, self).default_get(fields)
        model = self._context.get('active_model')
        active_id = self._context.get('active_id')
        if active_id and model == 'hr.applicant':
            record = self.env[model].browse(active_id)
            res.update({
                'applicant_id': record.id,
                'company_id': record.company_id.id,
                'emp_name': record.partner_name,
            })
        return res

    applicant_id = fields.Many2one(
        'hr.applicant',
        string="Applicant"
    )
    # employee_id = fields.Many2one(
    #     'hr.employee',
    #     string="Employee",
    #     required=True
    # )
    emp_name = fields.Char(string="Employee Name", required=True)

    salary = fields.Float(
        string="Monthly Salary",
        required=True
    )
    company_id = fields.Many2one(
        'res.company', 
        'Company', 
        required=True, 
    )
    currency_id = fields.Many2one(
        "res.currency", 
        related='company_id.currency_id', 
        string="Currency", 
        readonly=True, 
        required=True
    )

    def create_job_offer_request(self):
        vals = {
            'application_id': self.applicant_id.id,
            'company_id': self.company_id.id or self.env.company.id,
            'emp_name': self.emp_name,
            'monthly_salary': self.salary,
        }
        request_id = self.env['job.offer.customer'].create(vals)
        if request_id and self.applicant_id:
            self.applicant_id.custom_job_offer_id = request_id.id
        action = self.env.ref("job_offer_applicant_employee.action_custom_job_offer_customer").sudo().read()[0]
        action['views'] = [(self.env.ref('job_offer_applicant_employee.custom_job_offer_customer_form_view').id, 'form')]
        action['res_id'] = request_id.id
        return action