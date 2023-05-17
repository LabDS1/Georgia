# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import api, fields, models, _


class PurchaseOrder(models.Model):
    _inherit = "purchase.order"

    so_id = fields.Many2one(
        'sale.order', "Sale Order Id",
        compute='_compute_so_id'
    )

    def _compute_so_id(self):
        for rec in self:
            rec.so_id = rec._get_sale_orders() if rec._get_sale_orders() else False

    def _prepare_invoice(self):
        invoice_vals = super()._prepare_invoice()
        invoice_vals.update({'purchase_id': self.id})
        return invoice_vals


