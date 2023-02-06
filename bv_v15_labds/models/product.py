# -*- coding: utf-8 -*-
from odoo import fields, api, models, _


class ProductTemplate(models.Model):
    _inherit = "product.template"

    cost_not_to_update = fields.Boolean(string="Cost Not to Update")