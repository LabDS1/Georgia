# -*- coding: utf-8 -*-

from datetime import timedelta

from odoo import SUPERUSER_ID, api, fields, models, _
from odoo.exceptions import UserError, ValidationError
from odoo.tools import is_html_empty


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    # validy_date = fields

    def copy(self):
        res = super(SaleOrder, self).copy()
        res.write({'validity_date': fields.Datetime.now() + timedelta(days=30)}) 
        return res


    def update_optional_product_prices(self):
        """Callback for button on SO form which, when clicked updates the unit price of all products on the optional product lines."""

        # raise UserError(str('YEs'))
        self.ensure_one()
        lines_to_update = []
        standard_price_dic = {}

        for line in self.sale_order_option_ids:
            key = str(line.id)+'-'+str(line.product_id.id)
            standard_price_dic.update({key: line.product_id.standard_price})

        for line in self.sale_order_option_ids:
            product = line.product_id.with_context(
                partner=self.partner_id,
                quantity=line.quantity,
                date=self.date_order,
                pricelist=self.pricelist_id.id,
                uom=line.uom_id.id,
            )
            price_unit = self.env['account.tax']._fix_tax_included_price_company(
                line._get_display_price(product), line.product_id.taxes_id, line.tax_id, line.company_id)
            if self.pricelist_id.discount_policy == 'without_discount' and price_unit:

                price_discount_unrounded = self.pricelist_id.get_product_price(product, line.quantity, self.partner_id, self.date_order, line.uom_id.id)
                discount = max(0, (price_unit - price_discount_unrounded) * 100 / price_unit)
            else:
                discount = 0
            lines_to_update.append((1, line.id, {'price_unit': price_unit, 'discount': discount}))

        self.update({'sale_order_option_ids': lines_to_update})
        self.show_update_pricelist = False
        for key,value in standard_price_dic.items():
            for line in self.sale_order_option_ids:
                if key == (str(line.id)+'-'+str(line.product_id.id)):
                    line.product_id.standard_price = value
        self.message_post(body=_("Optional product prices have been recomputed according to pricelist <b>%s<b> ", self.pricelist_id.display_name))


    def update_optional_product_standard_price(self):
        """Method used in 'update_optional_product_prices' method to update a product's standard cost."""

        for line in self.sale_order_option_ids:
            if line.purchase_price and not line.product_id.cost_not_to_update:
                line.product_id.update({'standard_price': line.purchase_price})