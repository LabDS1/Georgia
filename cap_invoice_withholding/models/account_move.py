# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.tools import populate
from odoo.exceptions import UserError


import logging
import math
from functools import lru_cache
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)



class InvoiceMove(models.Model):
    _inherit = "account.move"

    def action_post(self):
        res = super(InvoiceMove, self).action_post()
        for inv in self:
            if inv.move_type in ['out_invoice','out_refund']:
                withholding = self.env['withholding.line'].search([('invoice_id','=',inv.id)],order="id desc", limit=1)
                if withholding:
                    so = inv.invoice_line_ids.mapped('sale_line_ids').mapped('order_id')
                    withholding.sale_order_id = so.id
        return res

