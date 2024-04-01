from odoo import api, Command, fields, models, _
from odoo.exceptions import UserError, ValidationError


class Project(models.Model):
    _inherit = "project.project" 

    move_to_done_stage = fields.Date(string='Done Date', 
                                     help="Default start date for this Analytic Account.")
    
    def _calculate_done_date(self):
        done_stage_id = self.env.ref('project.project_project_stage_2').id
        subtype_id = self.env.ref('project.mt_project_stage_change').id
        for record in self:
            if record.stage_id.id == done_stage_id:
                messages = self.env['mail.message'].search([('subtype_id','=',subtype_id),
                                                 ('res_id','=',record.id),
                                                 ('model','=','project.project')])
                
                message = messages.filtered(lambda msg: msg.tracking_value_ids[0].new_value_integer == done_stage_id)
                if message:
                    record.move_to_done_stage = message.create_date
                    