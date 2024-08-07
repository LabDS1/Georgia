# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.tools import html_keep_url, is_html_empty
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    withholding_ids = fields.One2many('withholding.line', 'sale_order_id', string='Withholdings', copy=True)

