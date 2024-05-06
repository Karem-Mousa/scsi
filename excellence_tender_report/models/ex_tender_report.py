from odoo import api, fields, models


class EXTenderReportWiz(models.TransientModel):
    _name = 'ex.tender.report.wiz'

    no_facility = fields.Char('رقم المنشاة')
    period_no = fields.Integer('لمدة')
    period_type = fields.Selection(
        [('day', 'يوم'), ('month', 'شهر'), ('year', 'سنة')]
    )
    type = fields.Selection([('tender', 'tender'), ('draft', 'draft')])

    def print_report(self):
        context = dict(self._context).copy()
        context['no_facility'] = self.no_facility
        context['type'] = self.type
        context['period_no'] = self.period_no
        context['period_type'] = str(dict(self._fields['period_type'].selection).get(self.period_type))
        return self.env.ref('excellence_tender_report.ex_report_action').report_action(
            self,
            data=context
        )
