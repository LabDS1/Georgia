from odoo import models, api
from odoo.tools import float_compare
import logging

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_avalara_taxes(self, commit):
        if self.add_withholding:
            # Step 1: Get Avalara tax data
            mapped_taxes, summary = self._map_avatax(commit)

            if commit:
                return

            # Step 2: Apply Avalara-calculated tax_ids and totals
            for line, detail in mapped_taxes.items():
                line.tax_ids = detail['tax_ids']
                line.price_total = detail['tax_amount'] + detail['total']

            self.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True)

            if not summary:
                return

            # Step 3: Correct mismatches unless custom withholding is applied
            for record in self:
                if record.add_withholding:
                    _logger.warning(
                        "[AVALARA SYNC] Skipping tax correction on move %s due to withholding logic.",
                        record.name or record.id
                    )
                    continue

                for tax, avatax_amount in summary[record].items():
                    tax_lines = record.line_ids.filtered(lambda l: l.tax_line_id == tax)
                    if not tax_lines:
                        continue

                    avatax_amount_currency = -avatax_amount
                    total_amt_cur = sum(t.amount_currency for t in tax_lines)

                    if float_compare(total_amt_cur, avatax_amount_currency,
                                     precision_rounding=record.currency_id.rounding) != 0:
                        correction = avatax_amount_currency - total_amt_cur
                        _logger.warning(
                            "[AVALARA SYNC] Tax mismatch on tax %s (move: %s). Expected: %s, Found: %s. Applying correction: %s",
                            tax.name, record.name or record.id, avatax_amount_currency, total_amt_cur, correction,
                        )

                        for line in tax_lines:
                            proportion = (line.amount_currency / total_amt_cur) if total_amt_cur else 1 / len(tax_lines)
                            line_correction = correction * proportion
                            new_amt_currency = line.amount_currency + line_correction

                            if line.currency_id == line.company_currency_id:
                                new_balance = new_amt_currency
                            else:
                                new_balance = line.balance + line.currency_id._convert(
                                    line_correction, line.company_currency_id,
                                    line.company_id, line.date
                                )

                            line.with_context(check_move_validity=False).write({
                                'amount_currency': new_amt_currency,
                                'balance': new_balance,
                                'debit': new_balance if new_balance > 0 else 0.0,
                                'credit': -new_balance if new_balance < 0 else 0.0,
                            })

                            _logger.info(
                                "[AVALARA SYNC] Updated tax line %s: amount_currency=%s, balance=%s",
                                line.id, new_amt_currency, new_balance
                            )
        else:
            super()._compute_avalara_taxes(commit)
