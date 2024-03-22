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
