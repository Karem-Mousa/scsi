from odoo import api, fields, models
import odoo.exceptions as odex


class MainApproveModel(models.AbstractModel):
    _name = 'main.approve.model'
    _inherit = ['mail.thread', 'mail.activity.mixin']
    _description = 'MainApproveModel'

    state = fields.Selection(selection=[
        ('draft', 'Draft'),
        ('approved', 'Approved'),
        ('validated', 'Validated'),
        ('refused', 'Refused'),
    ], default='draft')

    employee_id = fields.Many2one('hr.employee', string='إسم الموظف', required=1)

    dep_manager = fields.Many2one('res.users', related='employee_id.department_id.manager_id.user_id', store=True)

    is_validation_user = fields.Boolean(compute='_is_validation_user')

    def _is_validation_user(self):
        for rec in self:
            rec.is_validation_user = rec.env.user.has_group('bamco_emp_service_cycle_approve.validation_group')

    @api.model
    def create(self, vals):
        res = super().create(vals)
        if res.dep_manager:
            res.notify([res.dep_manager])
        return res

    def action_approve(self):
        users = self.env.ref('bamco_emp_service_cycle_approve.validation_group').users
        if users:
            self.notify(users)
            self.state = 'approved'
        else:
            raise odex.ValidationError('There\'s no users in "Validation Group"!')

    def action_validate(self):
        self.state = 'validated'

    def action_refuse(self):
        self.state = 'refused'

    def notify(self, users):
        base_url = self.env['ir.config_parameter'].sudo().get_param('web.base.url')
        base_url += '/web#id=%d&view_type=form&model=%s' % (self.id, self._name)
        message_text = f'<strong>Approve Required</strong> ' \
                       f'<p>This <a href=%s>Request</a> is need your approve!</p>' % base_url

        root = self.env['ir.model.data']._xmlid_to_res_id("base.partner_root")
        notification_ids = []
        for user in list(set(users)):
            notification_ids.append((0, 0, {
                'res_partner_id': user.partner_id.id,
                'notification_type': 'inbox'
            }))
        self.message_post(record_name='Sale Order Approve',
                          body=message_text,
                          message_type="notification",
                          subtype_xmlid="mail.mt_comment",
                          author_id=root,
                          notification_ids=notification_ids)
