# -*- coding: utf-8 -*-
from odoo import models, api, fields, _

class ProjectTask(models.Model):
    _inherit = "project.task"

    project_description = fields.Html(compute='_project_description',string='Project Description')

    def _project_description(self):
        if self.sudo().project_id:
            self.sudo().project_description = self.sudo().project_id.description
        else:
            self.sudo().project_description = False

