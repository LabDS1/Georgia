# -*- coding: utf-8 -*-
from odoo import models, api, fields, _

class ProjectTask(models.Model):
    _inherit = "project.task"

    project_description = fields.Html(compute='_project_description',string='Project Description')

    def _project_description(self):
        if self.project_id:
            self.project_description = self.project_id.description
        else:
            self.project_description = False

