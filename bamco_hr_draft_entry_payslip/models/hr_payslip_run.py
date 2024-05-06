from odoo import fields, models, api, _
import xlsxwriter
from io import BytesIO
import base64
from datetime import datetime
from odoo import exceptions


class HrPayslipRun(models.Model):
    _inherit = 'hr.payslip.run'

    account_entry_id = fields.Many2one('account.move', 'Accounting Entry')

    def action_validate(self):
        res = super(HrPayslipRun, self).action_validate()
        for rec in self.slip_ids:
            self.account_entry_id = rec.move_id.id
        return res
