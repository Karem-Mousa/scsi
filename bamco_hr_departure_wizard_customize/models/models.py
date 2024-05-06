from odoo import api, fields, models


class Depature(models.TransientModel):
    _inherit = 'hr.departure.wizard'

    attachment = fields.Binary(required=True)

    def action_register_departure(self):
        res = super().action_register_departure()
        employee_id = self.env.context.get('active_id')
        emp = self.env['hr.employee'].browse(employee_id)
        employee_attachment = self.env['ir.attachment'].create({
            'name': emp.name + 'Attachment',
            'type': 'binary',
            'datas': self.attachment,
            'res_model': 'hr.employee',
            'res_id': employee_id,
        })
        emp.contract_id.active = False
        return res
