# -*- coding: utf-8 -*-
from odoo import models, fields
from odoo.tools import populate

import logging
import math
from functools import lru_cache
from dateutil.relativedelta import relativedelta

_logger = logging.getLogger(__name__)



class WithHoldingLine(models.Model):
    # _inherit = ['withholding.line']
    _name = 'withholding.line'
    _inherit = ['withholding.line','mail.thread','mail.activity.mixin']

    sale_order_id = fields.Many2one('sale.order', string='Sales Order', tracking=True)

    partner_id = fields.Many2one('res.partner', 'Customer', required=True, tracking=True)
    project_id = fields.Many2one('project.project', 'Project', tracking=True)
    invoice_id = fields.Many2one('account.move', 'Invoice', tracking=True)
    payment_invoice_id = fields.Many2one('account.move', 'Payment Invoice', tracking=True)
    product_id = fields.Many2one('product.product', 'Product', required=True, tracking=True)