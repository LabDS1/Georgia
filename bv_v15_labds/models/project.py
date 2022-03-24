# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


class ProjectTask(models.Model):
    _inherit = "project.task"

    project_description = fields.Html(related='project_id.description', string='Project Description', store=True)
    project_descrip = fields.Html(string='Project Description')
