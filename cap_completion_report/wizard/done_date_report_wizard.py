from odoo import models, fields

class DoneDateReportWizard(models.TransientModel):
    _name = 'done.date.report.wizard'
    _description = 'Done Date Report Wizard'

    sale_order_numbers = fields.Char(string="Sale Orders", help="Enter Sale Order numbers separated by commas.")
    xlsx_output = fields.Binary(string='Excel Output', readonly=True)

    def generate_xls_report(self):
        """
        @public - Generate and download the report based on Sale Order numbers.
        """
        file, report_name = self.env['done.date.report']._generate_report(self.sale_order_numbers)
        self.update({'xlsx_output': file})
        # download excel report
        return {
            'type': 'ir.actions.act_url',
            'name': 'Done Date Report',
            'url': '/web/content/done.date.report.wizard/%s/xlsx_output/%s?download=true' % (
                self.id, report_name),
        }