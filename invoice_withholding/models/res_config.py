# -*- coding: utf-8 -*-

from odoo import fields, models, api
import werkzeug.urls


class ResCompany(models.Model):
    _inherit = "res.company"

    withholding_product_id = fields.Many2one('product.product', string='Withholding Product')
    withholding_percentage = fields.Float(string='Withholding Percentage')


class ResConfigSettings(models.TransientModel):
    _inherit = 'res.config.settings'

    withholding_product_id = fields.Many2one('product.product', related='company_id.withholding_product_id', string='Withholding Product', readonly=False)
    withholding_percentage = fields.Float(related='company_id.withholding_percentage', string='Withholding Percentage', readonly=False)

# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: