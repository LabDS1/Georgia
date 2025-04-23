import logging
from odoo import models, api
from odoo.tools import float_compare

_logger = logging.getLogger(__name__)

class AccountMove(models.Model):
    _inherit = "account.move"

    def _compute_avalara_taxes(self, commit):
        mapped_taxes, summary = self._map_avatax(commit)

        _logger.info("[AVALARA SYNC] Processing Avalara tax sync. Commit: %s", commit)

        if commit:
            _logger.info("[AVALARA SYNC] Commit=True, skipping tax corrections.")
            return

        for line, detail in mapped_taxes.items():
            _logger.debug("[AVALARA SYNC] Updating tax_ids and price_total for line %s", line.id)
            line.tax_ids = detail['tax_ids']
            line.price_total = detail['tax_amount'] + detail['total']

        self.with_context(check_move_validity=False)._recompute_dynamic_lines(recompute_all_taxes=True)

        if not summary:
            _logger.info("[AVALARA SYNC] No summary returned, nothing to check.")
            return

        for record in self:
            _logger.info("[AVALARA SYNC] Checking taxes on move %s", record.name or record.id)
            for tax, avatax_amount in summary[record].items():
                tax_lines = record.line_ids.filtered(lambda l: l.tax_line_id == tax)
                if not tax_lines:
                    _logger.warning("[AVALARA SYNC] No tax lines found for tax %s", tax.name)
                    continue

                avatax_amount_currency = -avatax_amount
                total_amt_cur = sum(t.amount_currency for t in tax_lines)

                if float_compare(total_amt_cur, avatax_amount_currency, precision_rounding=record.currency_id.rounding) != 0:
                    correction = avatax_amount_currency - total_amt_cur
                    line_to_fix = tax_lines[0]

                    _logger.warning(
                        "[AVALARA SYNC] Tax mismatch on tax %s (move: %s). Expected: %s, Found: %s. Applying correction: %s",
                        tax.name, record.name or record.id,
                        avatax_amount_currency, total_amt_cur, correction
                    )

                    new_amt_currency = line_to_fix.amount_currency + correction
                    if line_to_fix.currency_id == line_to_fix.company_currency_id:
                        new_balance = new_amt_currency
                    else:
                        new_balance = line_to_fix.currency_id._convert(
                            new_amt_currency, line_to_fix.company_currency_id,
                            line_to_fix.company_id, line_to_fix.date
                        )

                    line_to_fix.with_context(check_move_validity=False).write({
                        'amount_currency': new_amt_currency,
                        'balance': new_balance,
                        'debit': new_balance if new_balance > 0 else 0.0,
                        'credit': -new_balance if new_balance < 0 else 0.0,
                    })

                    _logger.info(
                        "[AVALARA SYNC] Corrected tax line %s: amount_currency=%s, balance=%s, debit=%s, credit=%s",
                        line_to_fix.id, new_amt_currency, new_balance,
                        new_balance if new_balance > 0 else 0.0,
                        -new_balance if new_balance < 0 else 0.0
                    )
                else:
                    _logger.info("[AVALARA SYNC] Tax line %s is already correct. Skipping.", tax_lines[0].id)
