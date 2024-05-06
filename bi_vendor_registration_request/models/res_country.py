# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models

class ResCountry(models.Model):
    _inherit = 'res.country'

    def get_country_states(self):
        return self.sudo().state_ids