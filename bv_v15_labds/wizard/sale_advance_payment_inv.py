# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

from odoo import models,_


class SaleAdvancePaymentInv(models.TransientModel):
    _inherit = "sale.advance.payment.inv"

    def _get_advance_details(self, order):

        context = {'lang': order.partner_id.lang}
        if self.advance_payment_method == 'percentage':
            amount = order.amount_untaxed * self.amount / 100
            name = _("Design and Engineering of %s%%") % (self.amount)
        else:
            amount = self.fixed_amount
            name = _('Design and Engineering')
        del context

        return amount, name



