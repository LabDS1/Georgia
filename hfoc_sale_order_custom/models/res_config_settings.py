# -*- coding: utf-8 -*-
from odoo import models, fields


class ResConfigSetting(models.TransientModel):
    _inherit = 'res.config.settings'

    hfoc_date_expiration = fields.Boolean(string="Default Date Expiration")
    hfoc_num = fields.Integer(string='Num', default=1 )
    
    
    hfoc_range_date = fields.Selection(
        string='Range',
        selection=[('months', 'Months'), ('weeks', 'Weeks'),('days', 'Days')],
        default='months'
    )
    

    def set_values(self):
        res=super(ResConfigSetting, self).set_values()
        self.env['ir.config_parameter'].set_param('hfoc_date_expiration', self.hfoc_date_expiration)
        self.env['ir.config_parameter'].set_param('hfoc_num', self.hfoc_num)
        self.env['ir.config_parameter'].set_param('hfoc_range_date', self.hfoc_range_date)
        return res
    
    def get_values(self):
        res = super(ResConfigSetting, self).get_values()
        hfoc_date_expiration = self.env['ir.config_parameter'].sudo().get_param('hfoc_date_expiration')
        hfoc_num = self.env['ir.config_parameter'].sudo().get_param('hfoc_num')
        hfoc_range_date = self.env['ir.config_parameter'].sudo().get_param('hfoc_range_date')
        res.update(
            hfoc_date_expiration=hfoc_date_expiration,
            hfoc_num=hfoc_num,
            hfoc_range_date=hfoc_range_date
        )
        return res

    