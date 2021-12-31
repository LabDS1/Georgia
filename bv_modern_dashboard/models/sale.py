# -*- coding: utf-8 -*-
from odoo import api, models, fields


class SaleOrder(models.Model):
    _inherit = 'sale.order'

    @api.model
    def get_quotation_draft(self):
        quotation = self.env['sale.order'].search_count([('state', '=', 'draft')])
        return quotation

    @api.model
    def get_sale_order_total(self):
        sale_order = self.env['sale.order'].search_count([('state', '=', 'sale')])
        return sale_order

    @api.model
    def get_quotation_sent(self):
        quotation_sent = self.env['sale.order'].search_count([('state', '=', 'sent')])
        return quotation_sent

    @api.model
    def get_quotation_cancel(self):
        quotation_cancel = self.env['sale.order'].search_count([('state', '=', 'cancel')])
        return quotation_cancel

    @api.model
    def get_customers(self):
        customers = self.env['sale.order'].search_count([('partner_id.customer_rank', '>=', 1)])
        return customers

    @api.model
    def get_to_be_invoiced(self):
        to_be_invoiced = self.env['sale.order'].search_count([('invoice_status', '=', 'to invoice')])
        return to_be_invoiced

    @api.model
    def get_fully_invoiced(self):
        fully_invoiced = self.env['sale.order'].search_count([('invoice_status', '=', 'invoiced')])
        return fully_invoiced

    # @contextmanager
    @api.model
    def get_top_orders(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT so.id as so_id, so.name AS so_number, rp.name AS customer_name, so.date_order AS so_date, so.amount_total AS amount_total
                FROM sale_order so, res_partner rp
                WHERE rp.id = so.partner_id AND so.company_id = ANY (array[%s])AND state IN ('sale', 'done')
                ORDER BY so.amount_total DESC
                /*ORDER BY so.name*/
                """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        # print("===>", result)
        return result

    @api.model
    def get_top_customers(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT DISTINCT c.name AS customer_name, c.id AS customer_id, sum(sale.amount_total) AS sale_total
                FROM res_partner c, sale_order sale
                WHERE c.id = sale.partner_id AND state IN ('sale', 'done') AND sale.company_id = ANY (array[%s])
                GROUP BY c.name, c.id
                ORDER BY sale_total DESC
                /*ORDER BY rp.name DESC*/
                """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def get_sent_quotations(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT so.id AS so_id, so.name AS so_number, rp.name AS customer_name, so.date_order AS so_date, so.commitment_date AS so_del
                FROM sale_order so, res_partner rp
                WHERE rp.id = so.partner_id AND so.company_id = ANY (array[%s]) AND so.state IN ('sent')
                """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def get_cancel_orders(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT so.id AS so_id, so.name AS so_number, rp.name AS customer_name, so.date_order AS so_date
                FROM sale_order so, res_partner rp
                WHERE rp.id = so.partner_id AND so.company_id = ANY (array[%s]) AND so.state IN ('cancel')
                """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def price_wise_products(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT DISTINCT(product_template.name) AS product_name, product_template.list_price AS price
                FROM sale_order_line
                inner join product_product on product_product.id=sale_order_line.product_id
                inner join product_template on product_product.product_tmpl_id = product_template.id
                WHERE sale_order_line.company_id = ANY (array[%s])
                GROUP BY product_template.id
                ORDER BY price DESC"""%(company_id)
            self.env.cr.execute(query)
            docs = self._cr.dictfetchall()
            product = []
            for record in docs:
                product.append(record.get('product_name'))
            sale_price = []
            for record in docs:
                sale_price.append(record.get('price'))
            result = [sale_price, product]
        except Exception as e:
            result = []
        return result

    @api.model
    def montly_sale_orders(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT DISTINCT to_char(date_order, 'MON-YYYY') AS date, (sum(amount_total)) AS revenue, to_char(date_order, 'YYYY-MM') AS year
                FROM sale_order sale
                WHERE sale.create_date IS NOT NULL AND sale.company_id = ANY (array[%s])
                GROUP BY date, year
                ORDER BY year DESC
                """%(company_id)
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            date = []
            for record in docs:
                date.append(record.get('date'))
            revenue = []
            for record in docs:
                revenue.append(record.get('revenue'))
            result = [revenue, date]

            # print(result)
        except Exception as e:
            result = []
        return result

    @api.model
    def top_sale_team(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT ct.name AS sales_team_name, sum(sale.amount_total) AS sale_total
                FROM crm_team ct, sale_order sale
                WHERE ct.id = sale.team_id AND sale.company_id = ANY (array[%s])
                GROUP BY ct.name
                """%(company_id)
            self.env.cr.execute(query)
            docs = self._cr.dictfetchall()
            name = []
            for record in docs:
                name.append(record.get('sales_team_name'))
            sale = []
            for record in docs:
                sale.append(record.get('sale_total'))
            result = [sale, name]
        except Exception as e:
            result = []
        return result

    @api.model
    def recent_customer(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT c.name AS partner_name, sum(sale.amount_total) AS sale_total, sale.date_order, c.id AS customer_id
                FROM res_partner c, sale_order sale
                WHERE c.id = sale.partner_id AND state IN ('sale', 'done') AND sale.company_id = ANY (array[%s])
                GROUP BY c.name,sale.date_order, c.id
                ORDER BY sale.date_order DESC LIMIT 5
                """%(company_id)
            self.env.cr.execute(query)
            docs = self._cr.dictfetchall()
            partner = []
            for record in docs:
                partner.append(record.get('partner_name'))
            customer_ids = [i.get('customer_id') for i in docs]
            sale = []
            for record in docs:
                sale.append(record.get('sale_total'))
            result = [sale, partner, customer_ids]
        except Exception as e:
            result = []
        # print("===>",result)
        return result

    @api.model
    def recent_5_sale_order(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT sale.name AS sale_name, sum(sale.amount_total) AS sale_total, sale.date_order, sale.id AS so_id
                FROM sale_order sale
                WHERE sale.state = 'sale' AND sale.company_id = ANY (array[%s])
                GROUP BY sale_name, sale.date_order, sale.id
                ORDER BY sale.date_order DESC LIMIT 5
                """%(company_id)
            self.env.cr.execute(query)
            docs = self._cr.dictfetchall()
            name = []
            for record in docs:
                name.append(record.get('sale_name'))
            sale = []
            so_ids = [record.get('so_id') for record in docs]
            for record in docs:
                sale.append(record.get('sale_total'))
            result = [sale, name, so_ids]
        except Exception as e:
            result = []
        return result

    @api.model
    def amount_wise_sale_order_ac_to_customer(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT DISTINCT sum(so.amount_total) AS total, c.name AS partner_name, c.id AS customer_id
                FROM sale_order so, res_partner c
                WHERE c.id = so.partner_id AND so.amount_total > 0 AND so.company_id = ANY (array[%s])
                GROUP BY c.name, customer_id
                ORDER BY c.name
                """%(company_id)
            self.env.cr.execute(query)
            docs = self._cr.dictfetchall()
            partner = []
            for record in docs:
                partner.append(record.get('partner_name'))
            customer_ids = [record.get('customer_id') for record in docs]
            amount_total = []
            for record in docs:
                amount_total.append(record.get('total'))
            result = [amount_total, partner, customer_ids]
            # print("====>", result)
        except Exception as e:
            result = []
        return result

    @api.model
    def count_wise_customer_sale_order(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT DISTINCT count(so.id) AS sale_id, c.name AS partner_name, so.partner_id AS customer_id
                FROM sale_order so, res_partner c
                WHERE c.id = so.partner_id AND so.company_id = ANY (array[%s])
                GROUP BY c.name, customer_id
                ORDER BY c.name
                """%(company_id)
            self.env.cr.execute(query)
            docs = self._cr.dictfetchall()
            partner = []
            for record in docs:
                partner.append(record.get('partner_name'))
            customer_ids = [record.get('customer_id') for record in docs]
            sale_count = []
            for record in docs:
                sale_count.append(record.get('sale_id'))
            result = [sale_count, partner, customer_ids]
        except Exception as e:
            result = []
        return result
