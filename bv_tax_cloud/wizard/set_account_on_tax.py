from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError

class SetAccountTax(models.TransientModel):
    _name = "set.account.tax"
    _description = "Set Account On Tax"


    account_id = fields.Many2one('account.account',string="Account")


    def set_account_on_tax_lines(self):
        if not self.account_id:
            raise ValidationError('Please Select the Tax...!!!')
        active_ids = self._context.get('active_ids')
        account_tax = self.env['account.tax'].search([('id','in',active_ids),('type_tax_use','=','sale')])
        if account_tax and self.account_id:
            for tax in account_tax:
                for rec in tax.invoice_repartition_line_ids:
                    if rec.repartition_type == 'tax' and not rec.account_id:
                        rec.account_id = self.account_id.id
                for rec in tax.refund_repartition_line_ids:
                    if rec.repartition_type == 'tax' and not rec.account_id:
                        rec.account_id = self.account_id.id