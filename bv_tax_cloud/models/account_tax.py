from odoo import models, fields, api, _

class AccountTax(models.Model):

    _inherit = 'account.tax'

    def set_account_on_tax_line(self):
        return {
            'type': 'ir.actions.act_window',
            'name': _('Set Account On Tax'),
            'res_model': "set.account.tax",
            'view_mode': 'form',
            'view_id': self.env.ref('bv_tax_cloud.set_account_on_tax_form_view').id,
            'target': 'new',
            'context': self.env.context,
        }