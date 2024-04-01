# -*- coding: utf-8 -*-
from odoo import models, fields


class ProgressBilling(models.TransientModel):
    _name = 'progress.billing.wizard'
    _description = 'Progress Billing Report'

    start_date = fields.Date(string="Start Date")
    end_date = fields.Date(string="End Date")
    xlsx_output = fields.Binary(string='Excel Output', readonly=True)

    def generate_xls_report(self):
        """
        @public - Generate and download customer list report
        """
        # get values from report data generate model
        file, report_name = self.env['progress.billing.report']._generate_report(self.start_date, self.end_date)
        self.update({'xlsx_output': file})
        # download excel report
        return {
            'type': 'ir.actions.act_url',
            'name': 'Progress Billing Report',
            'url': '/web/content/progress.billing.wizard/%s/xlsx_output/%s?download=true' % (
                self.id, report_name),
        }