# -*- coding: utf-8 -*-
from odoo import models, fields, api, _


class PurchaseOrder(models.Model):

    _inherit = 'purchase.order'

    @api.model
    def get_rfqs_count(self):
        rfqs_count = self.env['purchase.order'].search_count([('state', '=', 'draft')])
        return rfqs_count

    @api.model
    def get_total_purchase_order_count(self):
        total_purchase_count = self.env['purchase.order'].search_count([('state', '=', 'purchase')])
        return total_purchase_count

    @api.model
    def get_rfq_sent_count(self):
        rfq_sent_count = self.env['purchase.order'].search_count([('state', '=', 'sent')])
        return rfq_sent_count

    @api.model
    def get_purchase_cancel_count(self):
        purchase_cancel_count = self.env['purchase.order'].search_count([('state', '=', 'cancel')])
        return purchase_cancel_count

    @api.model
    def get_vendors_lst(self):
        partners = self.env['res.partner'].search([('supplier_rank', '=', '1')])
        vendors_count = self.env['res.partner'].search_count([('purchase_line_ids', '!=', False)])
        return vendors_count

    @api.model
    def get_to_be_shipped_count(self):
        purchase_orders = self.env['purchase.order'].search_count([('picking_ids.state', '=', 'assigned')])
        return purchase_orders

    @api.model
    def get_fully_shipped_count(self):
        purchase_orders = self.env['purchase.order'].search_count([('picking_ids.state', '=', 'done')])
        return purchase_orders

    @api.model
    def get_to_be_billed_count(self):
        purchase_orders = self.env['purchase.order'].search_count(
            [('state', '=', 'purchase'), ('invoice_status', '=', 'to invoice')])
        return purchase_orders

    @api.model
    def get_fully_billed_count(self):
        purchase_orders = self.env['purchase.order'].search_count([('state', '=', 'purchase'), ('invoice_status', '=', 'invoiced')])
        return purchase_orders

    @api.model
    def get_top_purchase_orders(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT po.name AS so_number, rp.name AS customer_name, po.date_order AS po_date, po.id AS po_id
                FROM purchase_order po, res_partner rp
                WHERE rp.id = po.partner_id 
                AND state IN ('purchase') AND po.company_id = ANY (array[%s])
                ORDER BY po.amount_total DESC
                """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def get_cancel_purchase_orders(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT po.name AS so_number, rp.name AS customer_name, po.date_order AS po_date, po.id AS po_id
                FROM purchase_order po, res_partner rp
                WHERE rp.id = po.partner_id AND po.company_id = ANY (array[%s])
                AND state IN ('cancel')
                """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def get_purchase_orders_fully_billed(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT po.name AS so_number, rp.name AS customer_name, po.date_order AS po_date, po.id AS po_id
                FROM purchase_order po, res_partner rp
                WHERE rp.id = po.partner_id 
                AND state IN ('purchase') AND po.company_id = ANY (array[%s])
                AND po.invoice_status = 'invoiced'
                """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def recent_vendores_graph(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT DISTINCT count(purchase.id) AS purchase_id, c.name AS partner_name, c.id AS vendor_id
                FROM purchase_order purchase, res_partner c 
                WHERE c.id = purchase.partner_id AND purchase.state = 'purchase' AND purchase.company_id = ANY (array[%s])
                GROUP BY c.name, c.id
                ORDER BY purchase_id DESC LIMIT 5"""%(company_id)
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            partner = []
            for record in docs:
                partner.append(record.get('partner_name'))
            vendor_ids = [record.get('vendor_id') for record in docs]
            purchase_count = []
            for record in docs:
                purchase_count.append(record.get('purchase_id'))
            result = [purchase_count, partner, vendor_ids]
            # print("===>", result)
        except Exception as e:
            result = []
        return result

    @api.model
    def get_top_10_purchase_order(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT po.name AS purchase_order_name, sum(po.amount_total) AS total, po.id AS po_id
                FROM purchase_order po WHERE po.state = 'purchase' AND po.amount_total > 0 AND po.company_id = ANY (array[%s])
                GROUP BY po.name, po.amount_total, po.id
                ORDER BY po.amount_total DESC LIMIT 5
                """%(company_id)
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            purchase_order_name = []
            for record in docs:
                purchase_order_name.append(record.get('purchase_order_name'))
            total_amount = []
            po_ids = [record.get('po_id') for record in docs]
            for record in docs:
                total_amount.append(record.get('total'))
            result = [total_amount, purchase_order_name, po_ids]
        except Exception as e:
            result = []
        return result

    @api.model
    def get_top_5_vendor_graph(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                    SELECT DISTINCT c.name AS partner_name, sum(po.amount_total) AS total, c.id AS partner_id
                    FROM purchase_order po, res_partner c
                    WHERE c.id = po.partner_id AND po.state = 'purchase' AND po.amount_total > 0 AND po.company_id = ANY (array[%s])
                    GROUP BY c.name, c.id
                    ORDER BY total DESC LIMIT 5 """ % (company_id)
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            partner = []
            for record in docs:
                partner.append(record.get('partner_name'))
            amt_total = []
            for record in docs:
                amt_total.append(record.get('total'))
            partner_ids = [record.get('partner_id') for record in docs]
            result = [amt_total, partner, partner_ids]
        except Exception as e:
            result = []
        return result

    @api.model
    def amount_wise_purchase_order_ac_to_vendor(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT DISTINCT sum(purchase.amount_total) AS total, c.name AS partner_name 
                FROM purchase_order purchase, res_partner c 
                WHERE c.id = purchase.partner_id AND purchase.amount_total > 0 AND purchase.company_id = ANY (array[%s]) GROUP BY c.name ORDER BY total DESC"""%(company_id)
            self.env.cr.execute(query)
            docs = self._cr.dictfetchall()
            partner = []
            for record in docs:
                partner.append(record.get('partner_name'))
            amount_total = []
            for record in docs:
                amount_total.append(record.get('total'))
            result = [amount_total, partner]
        except Exception as e:
            result = []
        return result


class ProductSupplierInfo(models.Model):

    _inherit = 'product.supplierinfo'

    @api.model
    def get_supplier_graph(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT supplier.name AS supplier_name, sum(supplier_info.price) AS total_price 
                FROM product_supplierinfo supplier_info, res_partner supplier 
                WHERE supplier_info.name = supplier.id AND supplier_info.price > 0 AND supplier_info.company_id = ANY (array[%s]) GROUP BY supplier.name ORDER BY supplier.name DESC
                """%(company_id)
            label = ''
            self.env.cr.execute(query)
            docs = self._cr.dictfetchall()
            price_lst = []
            for record in docs:
                price_lst.append(record.get('total_price'))
            partner = []
            for record in docs:
                partner.append(record.get('supplier_name'))
            result = [price_lst, partner, label]
        except Exception as e:
            result = []
        return result
