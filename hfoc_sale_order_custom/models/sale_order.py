# -*- coding: utf-8 -*-
from odoo import api, models
import pytz
import dateutil

class SaleOrder(models.Model):
    _inherit = 'sale.order'


    @api.onchange('date_order')
    def onchange_date_order(self):        
        for self in self:
            hfoc_date_expiration = self.env['res.config.settings'].get_values().get("hfoc_date_expiration")            
            hfoc_range_date = self.env['res.config.settings'].get_values().get("hfoc_range_date")
            hfoc_num = self.env['res.config.settings'].get_values().get("hfoc_num")
            if hfoc_date_expiration and self.date_order and hfoc_range_date:
                timezone = pytz.timezone(self.env.user.tz)
                if hfoc_range_date == 'months':
                    time = dateutil.relativedelta.relativedelta(months=int(hfoc_num))
                elif hfoc_range_date == 'weeks':
                    time = dateutil.relativedelta.relativedelta(weeks=int(hfoc_num))
                else:
                    time = dateutil.relativedelta.relativedelta(days=int(hfoc_num))
                date_order=(self.date_order+time).astimezone(timezone).replace(tzinfo=None)
                self.validity_date=date_order.date()


                