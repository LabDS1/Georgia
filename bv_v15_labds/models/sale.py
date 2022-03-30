# -*- coding: utf-8 -*-

from odoo import fields, api, models, _
from odoo.tools import html_keep_url, is_html_empty
from datetime import datetime


class SaleOrder(models.Model):
    _inherit = "sale.order"

    is_delivery_address_same = fields.Boolean(default=True, string='Is Delivery address same')

    @api.onchange('partner_id', 'is_delivery_address_same')
    def onchange_partner_id(self):
        if not self.partner_id:
            self.update({
                'partner_invoice_id': False,
                'partner_shipping_id': False,
                'fiscal_position_id': False,
            })
            return

        self = self.with_company(self.company_id)

        addr = self.partner_id.address_get(['delivery', 'invoice'])
        partner_user = self.partner_id.user_id or self.partner_id.commercial_partner_id.user_id
        values = {
            'pricelist_id': self.partner_id.property_product_pricelist and self.partner_id.property_product_pricelist.id or False,
            'payment_term_id': self.partner_id.property_payment_term_id and self.partner_id.property_payment_term_id.id or False,
            'partner_invoice_id': addr['invoice'],
            'partner_shipping_id': addr['delivery'] if self.is_delivery_address_same else '',
        }
        user_id = partner_user.id
        if not self.env.context.get('not_self_saleperson'):
            user_id = user_id or self.env.context.get('default_user_id', self.env.uid)
        if user_id and self.user_id.id != user_id:
            values['user_id'] = user_id

        if self.env['ir.config_parameter'].sudo().get_param('account.use_invoice_terms'):
            if self.terms_type == 'html' and self.env.company.invoice_terms_html:
                baseurl = html_keep_url(self.get_base_url() + '/terms')
                values['note'] = _('Terms & Conditions: %s', baseurl)
            elif not is_html_empty(self.env.company.invoice_terms):
                values['note'] = self.with_context(lang=self.partner_id.lang).env.company.invoice_terms
        if not self.env.context.get('not_self_saleperson') or not self.team_id:
            values['team_id'] = self.env['crm.team'].with_context(
                default_team_id=self.partner_id.team_id.id
            )._get_default_team_id(domain=['|', ('company_id', '=', self.company_id.id), ('company_id', '=', False)], user_id=user_id)
        self.update(values)

    def update_prices(self):
        self.ensure_one()
        lines_to_update = []
        standard_price_dic = {}
        product_list = []
        for line in self.order_line.filtered(lambda line: not line.display_type):
            key = str(line.id)+'-'+str(line.product_id.id)
            standard_price_dic.update({key: line.product_id.standard_price})
        for line in self.order_line.filtered(lambda line: not line.display_type):
            product = line.product_id.with_context(
                partner=self.partner_id,
                quantity=line.product_uom_qty,
                date=self.date_order,
                pricelist=self.pricelist_id.id,
                uom=line.product_uom.id,
            )
            price_unit = self.env['account.tax']._fix_tax_included_price_company(
                line._get_display_price(product), line.product_id.taxes_id, line.tax_id, line.company_id)
            if self.pricelist_id.discount_policy == 'without_discount' and price_unit:

                price_discount_unrounded = self.pricelist_id.get_product_price(product, line.product_uom_qty, self.partner_id, self.date_order, line.product_uom.id)
                discount = max(0, (price_unit - price_discount_unrounded) * 100 / price_unit)
            else:
                discount = 0
            lines_to_update.append((1, line.id, {'price_unit': price_unit, 'discount': discount}))
        self.update({'order_line': lines_to_update})
        self.show_update_pricelist = False
        for key,value in standard_price_dic.items():
            for line in self.order_line.filtered(lambda line: not line.display_type):
                if key == (str(line.id)+'-'+str(line.product_id.id)):
                    line.product_id.standard_price = value
        # line.product_id.standard_price = product._context.get('standard_price')
        self.message_post(body=_("Product prices have been recomputed according to pricelist <b>%s<b> ", self.pricelist_id.display_name))

    def update_product_standard_price(self):
        for line in self.order_line.filtered(lambda line: not line.display_type):
            if line.purchase_price:
                line.product_id.update({'standard_price': line.purchase_price})

    def action_confirm(self):
        res = super(SaleOrder, self).action_confirm()
        # subject = "Job Confirmed"
        # body = """ Hey here is your job confirmed""",
        # email = self.env['ir.mail_server'].build_email(
        #     email_from=self.env.user.email,
        #     email_to='wbrown@labds.com',
        #     subject=subject, body=body,
        # )
        # self.env['ir.mail_server'].send_email(email)
        ir_model_data = self.env['ir.model.data']
        try:
            template_id = ir_model_data._xmlid_lookup('bv_v15_labds.so_confirm_mail_template')[2]
        except ValueError:
            template_id = False
        if template_id:
            self.env['mail.template'].browse(template_id).send_mail(self.id)
        return res


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_display_price(self, product):
        # TO DO: move me in master/saas-16 on sale.order
        # awa: don't know if it's still the case since we need the "product_no_variant_attribute_value_ids" field now
        # to be able to compute the full price

        # it is possible that a no_variant attribute is still in a variant if
        # the type of the attribute has been changed after creation.
        no_variant_attributes_price_extra = [
            ptav.price_extra for ptav in self.product_no_variant_attribute_value_ids.filtered(
                lambda ptav:
                    ptav.price_extra and
                    ptav not in product.product_template_attribute_value_ids
            )
        ]
        if no_variant_attributes_price_extra:
            product = product.with_context(
                no_variant_attributes_price_extra=tuple(no_variant_attributes_price_extra)
            )

        if self.order_id.pricelist_id.discount_policy == 'with_discount':
            self.order_id.update_product_standard_price()
            return product.with_context(pricelist=self.order_id.pricelist_id.id, uom=self.product_uom.id).price
        product_context = dict(self.env.context, partner_id=self.order_id.partner_id.id, date=self.order_id.date_order, uom=self.product_uom.id)

        final_price, rule_id = self.order_id.pricelist_id.with_context(product_context).get_product_price_rule(product or self.product_id, self.product_uom_qty or 1.0, self.order_id.partner_id)
        base_price, currency = self.with_context(product_context)._get_real_price_currency(product, rule_id, self.product_uom_qty, self.product_uom, self.order_id.pricelist_id.id)
        if currency != self.order_id.pricelist_id.currency_id:
            base_price = currency._convert(
                base_price, self.order_id.pricelist_id.currency_id,
                self.order_id.company_id or self.env.company, self.order_id.date_order or fields.Date.today())
        # negative discounts (= surcharge) are included in the display price
        return max(base_price, final_price)

    @api.depends('product_id', 'company_id', 'currency_id', 'product_uom')
    def _compute_purchase_price(self):
        for line in self:
            if not line.product_id:
                line.purchase_price = 0.0
                continue
            line = line.with_company(line.company_id)
            product_cost =0.00
            if line.purchase_price:
                product_cost = line.purchase_price
            else:
                product_cost = line.product_id.standard_price
            line.purchase_price = line._convert_price(product_cost, line.product_id.uom_id)

class MailTracking(models.Model):
    _inherit = "mail.tracking.value"

    @api.model
    def create_tracking_values(self, initial_value, new_value, col_name, col_info, tracking_sequence, model_name):
        tracked = True

        field = self.env['ir.model.fields']._get(model_name, col_name)
        if not field:
            return

        values = {'field': field.id, 'field_desc': col_info['string'], 'field_type': col_info['type'],
                  'tracking_sequence': tracking_sequence}

        if col_info['type'] in ['integer', 'float', 'char', 'text', 'datetime', 'monetary']:
            values.update({
                'old_value_%s' % col_info['type']: initial_value,
                'new_value_%s' % col_info['type']: new_value
            })
        elif col_info['type'] == 'date':
            values.update({
                'old_value_datetime': initial_value and fields.Datetime.to_string(
                    datetime.combine(fields.Date.from_string(initial_value), datetime.min.time())) or False,
                'new_value_datetime': new_value and fields.Datetime.to_string(
                    datetime.combine(fields.Date.from_string(new_value), datetime.min.time())) or False,
            })
        elif col_info['type'] == 'boolean':
            values.update({
                'old_value_integer': initial_value,
                'new_value_integer': new_value
            })
        elif col_info['type'] == 'selection':
            values.update({
                'old_value_char': initial_value or '',
                'new_value_char': new_value and dict(col_info['selection'])[new_value] or ''
            })
        elif col_info['type'] == 'many2one':
            values.update({
                'old_value_integer': initial_value and initial_value.id or 0,
                'new_value_integer': new_value and new_value.id or 0,
                'old_value_char': initial_value and initial_value.sudo().name_get()[0][1] or '',
                'new_value_char': new_value and new_value.sudo().name_get()[0][1] or ''
            })
        else:
            tracked = False

        if tracked:
            return values
        return {}



