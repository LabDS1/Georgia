from odoo import api, fields, models, _


class AccountAsset(models.Model):
    _inherit = 'account.asset'

    @api.depends('bv_related_bills', 'bv_related_po', 'bv_related_invoices', 'bv_related_so')
    def _compute_related_account_move_po(self):
        for rec in self:
            rec.bv_related_bills = rec.original_move_line_ids.mapped(
                'move_id').ids if rec.original_move_line_ids.mapped('move_id') else False
            rec.bv_related_po = rec.original_move_line_ids.mapped('move_id').mapped(
                'purchase_id').name if rec.original_move_line_ids.mapped('move_id').mapped('purchase_id') else False

    @api.depends('bv_related_bills', 'bv_related_po', 'bv_related_invoices', 'bv_related_so')
    def _compute_related_account_move_so(self):
        for rec in self:
            rec.bv_related_invoices = rec.original_move_line_ids.mapped('move_id').mapped('purchase_id').mapped(
                'so_id').invoice_ids.ids if rec.original_move_line_ids.mapped('move_id').mapped(
                'purchase_id').mapped('so_id').invoice_ids else False
            rec.bv_related_so = rec.original_move_line_ids.mapped('move_id').mapped('purchase_id').mapped(
                'so_id').ids if rec.original_move_line_ids.mapped('move_id').mapped('purchase_id').mapped(
                'so_id') else False

    bv_related_bills = fields.Many2many('account.move', 'move_type', 'move_id',
                                        compute='_compute_related_account_move_po')
    bv_related_po = fields.Char(compute='_compute_related_account_move_po')
    bv_related_invoices = fields.Many2many('account.move', 'move_id', compute='_compute_related_account_move_so')
    bv_related_so = fields.Many2many('sale.order', compute='_compute_related_account_move_so')

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
