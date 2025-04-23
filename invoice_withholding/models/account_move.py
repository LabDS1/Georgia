from odoo import models, api
from odoo.tools.float_utils import float_compare


class AccountMove(models.Model):
    _inherit = 'account.move'

    def _compute_avalara_taxes(self, commit=False):
        """
        Override Avalara's tax computation to skip withholding lines.
        """
        mapped_taxes, summary = self._map_avatax(commit)

        # Don't change taxes if invoice is posted with commit
        if commit:
            return

        # Map Avalara tax data to invoice lines
        for line, detail in mapped_taxes.items():
            if not line.is_withholding:
                line.tax_ids = detail['tax_ids']
                line.price_total = detail['tax_amount'] + detail['total']

        self.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True)

        if not summary:
            return

        # Now verify tax amounts line-by-line
        for record in self:
            for tax, avatax_amount in summary[record].items():
                tax_line = record.line_ids.filtered(
                    lambda l: l.tax_line_id == tax and not l.is_withholding
                )
                if not tax_line:
                    continue  # Skip if no non-withholding tax line
                tax_line.ensure_one()

                avatax_amount_currency = -avatax_amount
                avatax_balance = (
                    avatax_amount_currency
                    if tax_line.currency_id == tax_line.company_currency_id else
                    tax_line.currency_id._convert(
                        avatax_amount,
                        tax_line.company_currency_id,
                        tax_line.company_id,
                        tax_line.date,
                    )
                )

                # Compare and correct tax amounts if needed
                if float_compare(
                    tax_line.amount_currency,
                    avatax_amount_currency,
                    precision_rounding=record.currency_id.rounding
                ) != 0:
                    tax_line.with_context(check_move_validity=False).write({
                        'amount_currency': avatax_amount_currency,
                        'debit': 0.0 if avatax_balance <= 0 else abs(avatax_balance),
                        'credit': abs(avatax_balance) if avatax_balance <= 0 else 0.0,
                    })
                    record.with_context(check_move_validity=False)._recompute_dynamic_lines()

                # Correct minor rounding differences
                elif not record.currency_id.is_zero(tax_line.amount_currency + avatax_amount):
                    tax_line.with_context(check_move_validity=False).write({
                        'amount_currency': avatax_amount_currency,
                        'debit': avatax_balance if avatax_balance < 0 else 0,
                        'credit': avatax_balance if avatax_balance > 0 else 0,
                    })
