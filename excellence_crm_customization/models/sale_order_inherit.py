from odoo import models, fields, api, tools, _
from odoo.exceptions import ValidationError



class ExcSaleOrderInherit(models.Model):
    _inherit = "sale.order"

    x_project_name = fields.Char(string="Project Name")
    state = fields.Selection(
        selection_add=[('first_approve', 'First Approve'), ('second_approve', 'Second Approve'), ('sale',)])

    def button_first_approve(self):
        self.write({'state': 'first_approve'})
        return {}

    def button_second_approve(self):
        self.write({'state': 'second_approve'})
        return {}

    @api.onchange('x_project_name')
    def related_analytic_account(self):
        if self.analytic_account_id:
            self.analytic_account_id.sudo().write({'name': self.x_project_name})
        else:
            name = self.x_project_name if self.x_project_name else self.name
            analytic_account_id = self.env['account.analytic.account'].create({'name': name,
                                                                               'code': name})
            self.analytic_account_id = analytic_account_id.id

    def write(self, values):
        if 'state' in values:
            if values['state'] == 'first_approve':
                if not (self.user_has_groups('excellence_crm_customization.group_sales_first_approve')):
                    raise ValidationError(_("This Action Is Allowed Only For `Sales First Approve` "))

            if values['state'] == 'second_approve':
                if not (self.user_has_groups('excellence_crm_customization.group_sales_second_approve')):
                    raise ValidationError(_("This Action Is Allowed Only For `Sales Second Approve` "))

        return super(ExcSaleOrderInherit, self).write(values)


class ExcSaleOrderLineInherit(models.Model):
    _inherit = "sale.order.line"

    def _timesheet_create_project_prepare_values(self):
        """Generate project values"""
        account = self.order_id.analytic_account_id
        if not account:
            self.order_id._create_analytic_account(prefix=self.product_id.default_code or None)
            account = self.order_id.analytic_account_id

        # create the project or duplicate one
        return {
            'name': '%s - %s' % (self.order_id.client_order_ref,
                                 self.order_id.name) if self.order_id.client_order_ref else self.order_id.name,
            'analytic_account_id': account.id,
            'partner_id': self.order_id.partner_id.id,
            'sale_line_id': self.id,
            'active': True,
            'company_id': self.company_id.id,
            'x_project_name': self.order_id.x_project_name
        }
