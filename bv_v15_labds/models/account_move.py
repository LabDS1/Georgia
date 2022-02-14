from odoo import models, fields,api,_


class AccountMove(models.Model):
    _inherit = 'account.move'

    customer_po = fields.Char(string='Customer PO#')
    account_id = fields.Many2one('account.account', string='Account', required=False)
