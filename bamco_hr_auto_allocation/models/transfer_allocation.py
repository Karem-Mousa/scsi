from odoo import models, fields, api, _
from datetime import date, datetime, time
from dateutil.relativedelta import relativedelta
from odoo.exceptions import ValidationError


class TransferAllocation(models.Model):
    _name = 'transfer.allocation'

    name = fields.Char("Transfer Allocation")
    transfer_from = fields.Many2many('hr.leave.type', required=True,
                                     domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    transfer_to = fields.Many2one('hr.leave.type', required=True,
                                  domain="['|',('company_id','=',False),('company_id','=',company_id)]")
    days = fields.Integer(required=True)
    date_from = fields.Date(compute="compute_date_from", store=True, required=False)
    date_to = fields.Date(required=True)
    done = fields.Boolean(copy=False)
    company_id = fields.Many2one('res.company', 'Company', default=lambda self: self.env.company, copy=False)
