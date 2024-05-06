from odoo import api, fields, models


class HRResignationRequest(models.Model):
    _name = 'hr.resignation.req'
    _inherit = ['hr.resignation.req', 'main.approve.model']

    def print_report(self):
        action = self.env.ref(
            'bamco_resignation.bamco_resignation_report').report_action(self)
        return action

    notes = fields.Text(
        string="ملاحظات المدير",
        required=False)


    hr_comment = fields.Text(
        string="ملاحظات شئون الموظفين",
        required=False)

    company_id = fields.Many2one(
        'res.company', 'Company', required=True,
        default=lambda s: s.env.company.id, index=True)

    process = fields.Text(default='لابد من تقديم الاستقالة قبل نهاية الخدمة الفعلية بشهرين، فى حال رغبة الموظف الاستقالة فى حينه سوف يتم خصم مدة الاخطار من نهاية المستحاقات النهائية . يجب على الموظف المستقيل انهاء اجراءات اخلاء الطرف من العهد العينية المالية',
        string="الاجراءات",
        required=False)

