from odoo import models, fields

class DoneDateReportWizard(models.TransientModel):
    _name = 'done.date.report.wizard'
    _description = 'Done Date Report Wizard'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    xlsx_output = fields.Binary(string='Excel Output', readonly=True)

    def generate_xls_report(self):
        """
        @public - Generate and download the report
        """
        file, report_name = self.env['done.date.report']._generate_report(self.start_date, self.end_date)
        self.update({'xlsx_output': file})
        # Download Excel report
        return {
            'type': 'ir.actions.act_url',
            'name': 'Done Date Report',
            'url': '/web/content/done.date.report.wizard/%s/xlsx_output/%s?download=true' % (
                self.id, report_name),
        }
