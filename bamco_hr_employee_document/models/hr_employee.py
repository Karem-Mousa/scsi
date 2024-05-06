from odoo import models, fields, api, _


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    national_id = fields.Binary(translate=True)
    cv = fields.Binary(translate=True)
    sc_certificate = fields.Binary(translate=True)
    non_disclosure_statement = fields.Binary(translate=True)

    document_ids = fields.One2many('hr.document', 'employee_id')

    @api.model
    def create(self, vals):
        res = super(HrEmployee, self).create(vals)
        documents_types = self.env['hr.document.type'].search([])
        for dt in documents_types:
            self.env['hr.document'].create({'type_id': dt.id, 'employee_id': res.id})
        return res
