from odoo import fields, models, api, _
from odoo.exceptions import UserError, ValidationError


class EXProjectTaskInherit(models.Model):
    _inherit = "project.task"

    management_approve = fields.Boolean()

    def open_applicant(self):
        return {
            'type': 'ir.actions.act_window',
            'name': 'Jobs - Recruitment Form',
            'view_mode': 'form',
            'res_model': 'hr.applicant',
            'target': 'current',
            'context': {
                'default_project_name': self.project_id.name,
                'default_task_name': self.name,
            },

        }

    def write(self, values):
        if 'stage_id' in values:
            if values['stage_id'] not in [52, 53, 56]:
                if not self.project_id.total_planned_amount:
                    raise ValidationError(_("يجب تحديد ميزانية المشروع أولا"))

            if values['stage_id'] in [99]:
                pos_state = self.env['purchase.order'].sudo().search([('task_id', '=', self.id)]).mapped('state')
                if pos_state and not all(state in ['purchase'] for state in pos_state):
                    raise ValidationError(_("يجب تأكيد ال po أولا"))
            if values['stage_id'] in [97]:
                if not self.management_approve:
                    raise ValidationError(_("'Management Approve Must be done First"))

        if 'management_approve' in values:
            if not (self.user_has_groups('excellences_project_inherit.group_management_approve')):
                raise ValidationError(_("This Action Is Allowed Only For `Management Approve Group` "))

        return super(EXProjectTaskInherit, self).write(values)


class HrApplicantInheritEx(models.Model):
    _inherit = 'hr.applicant'

    project_name = fields.Char(string="Project Name- اسم المشروع", required=False, )
    task_name = fields.Char(string="Contract Name- اسم العقد", required=False, )
    work_place = fields.Char(string="Work Place- مكان العمل", required=False, )
    basic_salary = fields.Integer(string="Basic Salary- الراتب الأساسي", required=False, )
    h_a = fields.Integer(string="Housing Allowance- بدل السكن", required=False, )
    t_a = fields.Integer(string="Transportation Allowance- بدل النقل", required=False, )
    net_salary = fields.Integer(string="Net Salary- صافي الراتب", required=False, )
    total_salary = fields.Integer(string="Total Salary- أجمالي الراتب", required=False, )
    h_e = fields.Char(string="Health Insurance- الرعاية الصحية", required=False,
                      default="According to Company Policy- حسب سياسة الشركة")
    d_c = fields.Char(string="Duration of the Contact-مدة العقد", required=False, default="One Year- سنة ميلادية")
    a_l = fields.Char(string="Annual Leave- الإجازة السنوة", required=False, default="21 days in year- 21 يوم في السنة")
    w_h = fields.Char(string="Work Hours- ساعات العمل", required=False,
                      default="8 hours a day // 5 days a week- 8 ساعات يوميا // 5 أيام في الأسبوع")
    gossi = fields.Char(string="GOSI- التأمينات الاجتماعية", required=False,
                        default="According to GOSI Policy- حسب سياسة التأمينات الاجتماعية")
    probation = fields.Char(string="Probation- فترة التجربة", required=False, default="90 يوما- Days")
    offer_details = fields.Text(string="Offer Details- بيانات العرض", required=False,
                                default="1-العرض ساري لمدة 5 أيام من تاريخه // 2- هذا العرض لا يشكل أي التزام على الشركة إلى أن يتم توقيع العقد واستكمال الإجراءات")
