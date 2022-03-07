# -*- coding: utf-8 -*-
from odoo import models, api, fields, _


PROJECT_TASK_READABLE_FIELDS = {
    'id',
    'active',
    'description',
    'priority',
    'kanban_state_label',
    'project_id',
    'display_project_id',
    'color',
    'partner_is_company',
    'commercial_partner_id',
    'allow_subtasks',
    'subtask_count',
    'child_text',
    'is_closed',
    'email_from',
    'create_date',
    'write_date',
    'company_id',
    'displayed_image_id',
    'display_name',
    'portal_user_names',
    'legend_normal',
    'legend_blocked',
    'legend_done',
    'project_description',
}

PROJECT_TASK_WRITABLE_FIELDS = {
    'name',
    'partner_id',
    'partner_email',
    'user_ids',
    'date_deadline',
    'tag_ids',
    'sequence',
    'stage_id',
    'kanban_state',
    'child_ids',
    'parent_id',
    'priority',
    'project_description',
}


class ProjectTask(models.Model):
    _inherit = "project.task"

    project_description = fields.Html(related='project_id.description', string='Project Description', store=True)

    @property
    def SELF_READABLE_FIELDS(self):
        return PROJECT_TASK_READABLE_FIELDS | self.SELF_WRITABLE_FIELDS

    @property
    def SELF_WRITABLE_FIELDS(self):
        return PROJECT_TASK_WRITABLE_FIELDS
    
