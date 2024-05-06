# -*- coding: utf-8 -*-

from odoo import models, fields, api
import logging
import math

_logger = logging.getLogger(__name__)

try:
    from num2words import num2words
except ImportError:
    _logger.warning("The num2words python library is not installed, amount-to-text features won't be fully available.")
    num2words = None


class EXTenderInherit(models.Model):
    _inherit = 'excellence.tenders.minutes'

    def action_open_print_wiz(self):
        self.ensure_one()
        return {
            'name': 'Report Data',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'ex.tender.report.wiz',
            'context': {'active_id': self.id,
                        'default_no_facility': self.selected_company.x_commercial_register_num,
                        'default_type': 'tender'
                        },
            'target': 'new',

        }

    def action_open_print_draft_wiz(self):
        self.ensure_one()
        return {
            'name': 'Report Data',
            'type': 'ir.actions.act_window',
            'view_mode': 'form',
            'res_model': 'ex.tender.report.wiz',
            'context': {'active_id': self.id,
                        'default_no_facility': self.selected_company.x_commercial_register_num,
                        'default_type': 'draft'
                        },
            'target': 'new',

        }

    def num2letter(self, value):
        pre = float(value)
        text = ''

        dec_num = int(round(math.modf(pre)[0], 2) * 100)
        ent_num = int(round(math.modf(pre)[1]))

        text += num2words(ent_num, lang='ar')
        text += ' ريال '
        if dec_num != 0:
            text += ' و '
            text += num2words(dec_num, lang='ar')
            text += ' هللة'

        text += ' فقط لا غير '
        return text


class EXTendersLine(models.Model):
    _inherit = 'excellence.tenders.minutes.line'

    date = fields.Date('التاريخ')
