# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import SUPERUSER_ID, api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import is_html_empty


class SaleOrderOption(models.Model):
    _inherit = 'sale.order.option'

    company_id = fields.Many2one(related='order_id.company_id', string='Company', store=True, index=True)
    currency_id = fields.Many2one(related='order_id.currency_id', depends=['order_id.currency_id'], store=True, string='Currency')
    price_subtotal = fields.Monetary(compute='_compute_amount', string='Subtotal', store=True)
    price_tax = fields.Float(compute='_compute_amount', string='Total Tax', store=True)
    price_total = fields.Monetary(compute='_compute_amount', string='Total', store=True)
    tax_id = fields.Many2many('account.tax', string='Taxes', context={'active_test': False}, check_company=True)
    


    @api.depends('quantity', 'discount', 'price_unit', 'tax_id')
    def _compute_amount(self):
        """
        Compute the amounts of the SO line.
        """
        for line in self:
            price = line.price_unit * (1 - (line.discount or 0.0) / 100.0)
            taxes = line.tax_id.compute_all(price, line.order_id.currency_id, line.quantity, product=line.product_id, partner=line.order_id.partner_shipping_id)
            line.update({
                'price_tax': sum(t.get('amount', 0.0) for t in taxes.get('taxes', [])),
                'price_total': taxes['total_included'],
                'price_subtotal': taxes['total_excluded'],
            })
