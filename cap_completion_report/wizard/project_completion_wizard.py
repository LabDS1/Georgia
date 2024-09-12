# -*- coding: utf-8 -*-
from odoo import models, fields


class ProjectCompletion(models.TransientModel):
    _name = 'project.completion.wizard'
    _description = 'Project Completion Report'

    start_date = fields.Date(string="Start Date", required=True)
    end_date = fields.Date(string="End Date", required=True)
    xlsx_output = fields.Binary(string='Excel Output', readonly=True)

    def generate_xls_report(self):
        """
        @public - Generate and download the report
        """
        file, report_name = self.env['project.completion.report']._generate_report(self.start_date, self.end_date)
        self.update({'xlsx_output': file})
        # download excel report
        return {
            'type': 'ir.actions.act_url',
            'name': 'Project Completion Report',
            'url': '/web/content/project.completion.wizard/%s/xlsx_output/%s?download=true' % (
                self.id, report_name),
        }