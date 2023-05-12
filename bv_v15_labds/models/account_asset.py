from odoo import api, fields, models, _


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    def view_bill_list(self):
        move_line = self.original_move_line_ids.mapped('move_id').ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Related Bills',
            'view_mode': 'tree,form',
            'res_model': 'account.move',
            'domain': [('id', 'in', move_line)],
            'context': {'create': False},
            'target': 'new',
        }

    def view_po(self):
        move_ids = self.original_move_line_ids.mapped('move_id').mapped('purchase_id').ids
        return {
            'type': 'ir.actions.act_window',
            'name': 'Related PO',
            'view_mode': 'tree,form',
            'res_model': 'purchase.order',
            'domain': [('id', 'in', move_ids)],
            'context': {'create': False},
            'target': 'new'
        }
