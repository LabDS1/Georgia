# -*- coding: utf-8 -*-
from odoo import api, fields, models, tools, SUPERUSER_ID, _
from odoo.exceptions import UserError, ValidationError, AccessError


class ProjectTask(models.Model):
    _inherit = "project.task"

    project_description = fields.Html(related='project_id.description',string='Project Description', store=True)

    def _ensure_fields_are_accessible(self, fields, operation='read', check_group_user=True):

        assert operation in ('read', 'write'), 'Invalid operation'
        if fields and (not check_group_user or self.env.user.has_group('base.group_portal')) and not self.env.su:
            unauthorized_fields = set(fields) - (self.SELF_READABLE_FIELDS if operation == 'read' else self.SELF_WRITABLE_FIELDS)
            if unauthorized_fields and not ('project_description' in unauthorized_fields):
                raise AccessError(_('You cannot %s %s fields in task.', operation if operation == 'read' else '%s on' % operation, ', '.join(unauthorized_fields)))
