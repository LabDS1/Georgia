from odoo import models, api
from odoo.tools import float_compare

class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_avalara_taxes(self, commit):
        # Call the original logic to get the mapped taxes + summary
        mapped_taxes, summary = self._map_avatax(commit)

        if commit:
            return

        for line, detail in mapped_taxes.items():
            line.tax_ids = detail['tax_ids']
            line.price_total = detail['tax_amount'] + detail['total']
        self.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True)

        if not summary:
            return

        for record in self:
            for tax, avatax_amount in summary[record].items():
                tax_lines = record.line_ids.filtered(lambda l: l.tax_line_id == tax)
                if not tax_lines:
                    continue

                # Aggregate values
                total_amt_cur = sum(t.amount_currency for t in tax_lines)
                total_balance = sum(t.balance for t in tax_lines)
                avatax_amount_currency = -avatax_amount

                if float_compare(total_amt_cur, avatax_amount_currency, precision_rounding=record.currency_id.rounding) != 0:
                    correction = avatax_amount_currency - total_amt_cur
                    line_to_fix = tax_lines[0]
                    line_to_fix.with_context(check_move_validity=False).write({
                        'amount_currency': line_to_fix.amount_currency + correction,
                        'balance': line_to_fix.balance + (
                            correction if line_to_fix.currency_id == line_to_fix.company_currency_id
                            else line_to_fix.currency_id._convert(
                                correction, line_to_fix.company_currency_id,
                                line_to_fix.company_id, line_to_fix.date
                            )
                        )
                    })
