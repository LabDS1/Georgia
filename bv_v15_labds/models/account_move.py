from odoo import models, fields,api,_


class AccountMove(models.Model):
    _inherit = 'account.move'

    customer_po = fields.Char(string='Customer PO#')
