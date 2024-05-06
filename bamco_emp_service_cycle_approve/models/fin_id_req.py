from odoo import api, fields, models


class FinIDReq(models.Model):
    _name = 'financial.identification.request'
    _inherit = ['financial.identification.request', 'main.approve.model']

    def print_report(self):
        action = self.env.ref(
            'bamco_financial_identification_request.financial_identification_request_report').report_action(self)
        return action

    comment = fields.Text(
        string="افادة",
        default='نفيدكم بأن الموظف بياناته أعلاه أحد منسوبى شركة التميز لحلول الأعمال ولا يزال على رأس العمل حتى تاريخه، وقد منح هذا التعريف بناء على طلبه دون أدنى مسئولية على الشركة ، شاكرين ومقدرين لكم على الدوام حسن تعاونكم معنا وجل اهتمامكم بنا وتفضلوا بقبول وافر الاحترام والتقدير ،،،،',
        required=False)


class ManIDReq(models.Model):
    _name = 'managerial.identification.request'
    _inherit = ['managerial.identification.request', 'main.approve.model']

    def print_report(self):
        action = self.env.ref(
            'bamco_financial_identification_request.managerial_identification_request_report').report_action(self)
        return action

    comment = fields.Text(
        string="افادة",
        default='نفيدكم بأن الموظف بياناته أعلاه أحد منسوبى شركة التميز لحلول الأعمال ولا يزال على رأس العمل حتى تاريخه، وقد منح هذا التعريف بناء على طلبه دون أدنى مسئولية على الشركة ، شاكرين ومقدرين لكم على الدوام حسن تعاونكم معنا وجل اهتمامكم بنا وتفضلوا بقبول وافر الاحترام والتقدير ،،،،',
        required=False)
