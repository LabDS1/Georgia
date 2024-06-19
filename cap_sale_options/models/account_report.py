from odoo import api, fields, models
from odoo.exceptions import UserError


class CrmLead(models.Model):
    """Class extension of base model crm.lead."""

    _inherit = 'crm.lead'


    analytic_account_id = fields.Many2one('account.analytic.account')

    def action_new_quotation(self):
        """Extension of base method, action_new_quotation."""

        action = super().action_new_quotation()

        # Check if there is a analytic account associated with this opportunity. If not, create and link account to opportunity
        if not self.analytic_account_id:
            account = self.env['account.analytic.account'].create({'name': self.name})
            self.analytic_account_id = account
        
        # Update action to include default analytic account value in defaults via context
        action.get('context').update({'default_analytic_account_id': self.analytic_account_id.id})

        return action
        