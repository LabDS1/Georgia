# -*- coding: utf-8 -*-

from odoo import fields, models, _ , api
from odoo.exceptions import UserError, ValidationError


class Message(models.Model):
    _inherit = 'mail.message'
    @api.model
    def create(self, values_list):
        done_stage_id = self.env.ref('project.project_project_stage_2').id
        subtype_id = self.env.ref('project.mt_project_stage_change').id
        records = super().create(values_list)
        for rec in records:
            if rec.subtype_id.id == subtype_id:
                if rec.tracking_value_ids[0].new_value_integer == done_stage_id:
                    related_project = self.env['project.project'].browse(rec.res_id)
                    related_project.move_to_done_stage = rec.create_date
           
        return records
    