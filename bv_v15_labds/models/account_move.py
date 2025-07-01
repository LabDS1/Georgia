import datetime
import logging

from odoo import api, fields, models, _
from odoo.exceptions import ValidationError, UserError
from odoo.tools import float_compare, float_round
from odoo.tests.common import Form

_logger = logging.getLogger(__name__)


class AccountMove(models.Model):
    _inherit = 'account.move'

    customer_po = fields.Char(string='Customer PO#')
    purchase_vendor_bill_id = fields.Many2one('purchase.bill.union', store=True, readonly=True,
                                              states={'draft': [('readonly', False)]},
                                              string='Auto-complete',
                                              help="Auto-complete from a past bill / purchase order.")
    purchase_id = fields.Many2one('purchase.order', store=True, readonly=True,
                                  states={'draft': [('readonly', False)]},
                                  string='Purchase Order',
                                  help="Auto-complete from a past purchase order.")

    active = fields.Boolean(default=True)

    @api.onchange('purchase_vendor_bill_id', 'purchase_id')
    def _onchange_purchase_auto_complete(self):
        ''' Load from either an old purchase order, either an old vendor bill.

        When setting a 'purchase.bill.union' in 'purchase_vendor_bill_id':
        * If it's a vendor bill, 'invoice_vendor_bill_id' is set and the loading is done by '_onchange_invoice_vendor_bill'.
        * If it's a purchase order, 'purchase_id' is set and this method will load lines.

        /!\ All this not-stored fields must be empty at the end of this function.
        '''
        if self.purchase_vendor_bill_id.vendor_bill_id:
            self.invoice_vendor_bill_id = self.purchase_vendor_bill_id.vendor_bill_id
            self._onchange_invoice_vendor_bill()
        elif self.purchase_vendor_bill_id.purchase_order_id:
            self.purchase_id = self.purchase_vendor_bill_id.purchase_order_id
        # self.purchase_vendor_bill_id = False

        if not self.purchase_id:
            return

        # Copy data from PO
        invoice_vals = self.purchase_id.with_company(self.purchase_id.company_id)._prepare_invoice()
        invoice_vals['currency_id'] = self.line_ids and self.currency_id or invoice_vals.get('currency_id')
        del invoice_vals['ref']
        self.update(invoice_vals)

        # Copy purchase lines.
        po_lines = self.purchase_id.order_line - self.line_ids.mapped('purchase_line_id')
        new_lines = self.env['account.move.line']
        sequence = max(self.line_ids.mapped('sequence')) + 1 if self.line_ids else 10
        for line in po_lines.filtered(lambda l: not l.display_type):
            line_vals = line._prepare_account_move_line(self)
            line_vals.update({'sequence': sequence})
            new_line = new_lines.new(line_vals)
            sequence += 1
            new_line.account_id = new_line._get_computed_account()
            new_line._onchange_price_subtotal()
            new_lines += new_line
        new_lines._onchange_mark_recompute_taxes()

        # Compute invoice_origin.
        origins = set(self.line_ids.mapped('purchase_line_id.order_id.name'))
        self.invoice_origin = ','.join(list(origins))

        # Compute ref.
        refs = self._get_invoice_reference()
        self.ref = ', '.join(refs)

        # Compute payment_reference.
        if len(refs) == 1:
            self.payment_reference = refs[0]

        # self.purchase_id = False
        self._onchange_currency()

    def action_customer_po_update(self):
        account_move_ids = self.env['account.move'].search([('x_studio_customer_po', '!=', False),('move_type', 'in', ('out_invoice', 'out_refund','out_receipt'))])
        for rec in account_move_ids:
            rec.customer_po = rec.x_studio_customer_po

    def validate_taxes_on_invoice(self):
        self.ensure_one()
        company = self.company_id
        shipper = company or self.env.company
        api_id = shipper.taxcloud_api_id
        api_key = shipper.taxcloud_api_key
        request = self._get_TaxCloudRequest(api_id, api_key)

        request.set_location_origin_detail(shipper)
        request.set_location_destination_detail(
            self.env['res.partner'].browse(self._get_invoice_delivery_partner_id()))

        request.set_invoice_items_detail(self)

        response = request.get_all_taxes_values()

        if response.get('error_message'):
            raise ValidationError(
                _('Unable to retrieve taxes from TaxCloud: ') + '\n' +
                response['error_message']
            )

        tax_values = response['values']

        # warning: this is tightly coupled to TaxCloudRequest's _process_lines method
        # do not modify without syncing the other method
        raise_warning = False
        taxes_to_set = []
        for index, line in enumerate(self.invoice_line_ids.filtered(lambda l: not l.display_type)):
            if line._get_taxcloud_price() >= 0.0 and line.quantity >= 0.0:
                price = line.price_unit * (1 - (line.discount or 0.0) / 100.0) * line.quantity
                if not price:
                    tax_rate = 0.0
                else:
                    tax_rate = tax_values[index] / price * 100
                if len(line.tax_ids) != 1 or float_compare(line.tax_ids.amount, tax_rate, precision_digits=3):
                    raise_warning = True
                    tax_rate = float_round(tax_rate, precision_digits=3)
                    tax = self.env['account.tax'].sudo().with_context(active_test=False).search([
                        ('amount', '=', tax_rate),
                        ('amount_type', '=', 'percent'),
                        ('type_tax_use', '=', 'sale'),
                        ('company_id', '=', company.id),
                    ], limit=1)
                    if tax:
                        # Only set if not already set, otherwise it triggers a
                        # needless and potentially heavy recompute for
                        # everything related to the tax.
                        if not tax.active:
                            tax.active = True  # Needs to be active to be included in invoice total computation
                    else:
                        tax = self.env['account.tax'].sudo().with_context(default_company_id=company.id).create({
                            'name': 'Tax %.3f %%' % (tax_rate),
                            'amount': tax_rate,
                            'amount_type': 'percent',
                            'type_tax_use': 'sale',
                            'description': 'Sales Tax',
                        })
                    taxes_to_set.append((index, tax))

        with Form(self) as move_form:
            for index, tax in taxes_to_set:
                with move_form.invoice_line_ids.edit(index) as line_form:
                    line_form.tax_ids.clear()
                    if not line_form.display_type:
                        line_form.tax_ids.add(tax)

        if self.env.context.get('taxcloud_authorize_transaction'):
            reporting_date = self.get_taxcloud_reporting_date()

            if self.move_type == 'out_invoice':
                request.client.service.AuthorizedWithCapture(
                    request.api_login_id,
                    request.api_key,
                    request.customer_id,
                    request.cart_id,
                    self.id,
                    reporting_date,  # DateAuthorized
                    reporting_date,  # DateCaptured
                )
            elif self.move_type == 'out_refund':
                request.set_invoice_items_detail(self)
                origin_invoice = self.reversed_entry_id
                if origin_invoice:
                    request.client.service.Returned(
                        request.api_login_id,
                        request.api_key,
                        origin_invoice.id,
                        request.cart_items,
                        fields.Datetime.from_string(self.invoice_date)
                    )
                else:
                    _logger.warning(
                        "The source document on the refund is not valid and thus the refunded cart won't be logged on your taxcloud account.")

        if raise_warning:
            return {'warning': _('The tax rates have been updated, you may want to check it before validation')}
        else:
            return True