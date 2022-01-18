# -*- coding: utf-8 -*-
from odoo import models, fields, api, _
import datetime
from datetime import datetime
from dateutil.relativedelta import relativedelta


class AccountMove(models.Model):

    _inherit = 'account.move'

    @api.model
    def get_invoice_open(self):
        open_invoices = self.env['account.move'].search_count([('payment_state', '=', 'not_paid'),('state', '=', 'posted'),('move_type','=','out_invoice')])
        return open_invoices

    @api.model
    def get_bill_open(self):
        open_invoices = self.env['account.move'].search_count(
            [('payment_state', '=', 'not_paid'), ('state', '=', 'posted'), ('move_type', '=', 'in_invoice')])
        return open_invoices

    @api.model
    def get_invoice_cancel(self):
        cancel_invoices = self.env['account.move'].search_count([('state', '=', 'cancel')])
        return cancel_invoices

    @api.model
    def get_customer_invoice_paid_invoice_list(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT am.name AS move_number, c.name AS partner_name, am.amount_total AS move_total
                FROM account_move am, res_partner c
                WHERE c.id = am.partner_id AND am.company_id = ANY (array[%s])
                AND am.payment_state = 'paid'
                AND am.move_type= 'out_invoice'
            """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def get_vendor_invoice_paid_invoice_list(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT am.name AS move_number, c.name AS partner_name, am.amount_total as move_total
                FROM account_move am, res_partner c
                WHERE c.id = am.partner_id AND am.company_id = ANY (array[%s])
                AND am.payment_state = 'paid'
                AND am.move_type= 'in_invoice'
            """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def get_customers_lst(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT DISTINCT c.name AS partner_name, sum(am.amount_total) AS total
                FROM res_partner c, account_move am
                WHERE c.id = am.partner_id AND c.customer_rank >= 1 AND am.amount_total > 0 AND am.company_id = ANY (array[%s])
                GROUP BY c.name 
                ORDER BY total DESC
            """%(company_id)
            # query = """
            #     SELECT DISTINCT c.name AS partner_name
            #     FROM account_move am, res_partner c
            #     WHERE c.id = am.partner_id AND am.company_id = ANY (array[%s])
            #     AND (c.customer_rank = 1 OR c.customer_rank > 1)
            #     -- AND am.move_type= 'out_invoice'
            # """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def get_vendors_lst(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT DISTINCT c.name AS vendor_name, sum(am.amount_total) AS total
                FROM account_move am, res_partner c
                WHERE c.id = am.partner_id AND am.amount_total > 0 AND c.supplier_rank >= 1 AND am.company_id = ANY (array[%s]) 
                GROUP BY c.name 
                ORDER BY total DESC
                -- AND am.move_type= 'in_invoice'
            """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def get_customer_data_for_chart(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT DISTINCT c.name AS partner_name, sum(am.amount_total) AS total, c.id AS partner_id
                FROM account_move am, res_partner c
                WHERE c.id = am.partner_id AND am.amount_total > 0 
                AND am.company_id = ANY (array[%s]) AND c.customer_rank >= 1 
                GROUP BY c.name,c.id
                ORDER BY total DESC LIMIT 5
                -- AND am.move_type= 'out_invoice'
            """%(company_id)
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            partner = []
            for record in docs:
                partner.append(record.get('partner_name'))
            total_amount = []
            for record in docs:
                total_amount.append(record.get('total'))
            partner_ids = [record.get('partner_id') for record in docs]
            result = [total_amount, partner,partner_ids]
            # self.env.cr.execute(query)
            # result = [line.get('partner_name') for line in self.env.cr.dictfetchall()]
        except Exception as e:
            result = []
        return result

    @api.model
    def get_age_payable(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT  res_partner.name as due_partner, account_move.partner_id as parent,sum(account_move.amount_total) as amount from account_move, res_partner 
                WHERE account_move.partner_id = res_partner.id
                AND account_move.move_type = 'in_invoice'
                AND payment_state = 'not_paid'
                AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
                AND account_move.partner_id = res_partner.commercial_partner_id
                AND account_move.company_id = ANY (array[%s])
                GROUP BY parent, due_partner
                ORDER BY amount DESC 
            """%(company_id)
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            partner = []
            for record in docs:
                partner.append(record.get('due_partner'))
            total_amount = []
            for record in docs:
                total_amount.append(record.get('amount'))
            result = [total_amount, partner]
        except Exception as e:
            result = []
        return result

    @api.model
    def get_age_receivable(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT res_partner.name as bill_partner, account_move.partner_id as parent,sum(account_move.amount_total) as amount from account_move, res_partner where account_move.partner_id = res_partner.id
                AND account_move.move_type = 'out_invoice'
                AND payment_state = 'not_paid'
                AND Extract(YEAR FROM account_move.invoice_date_due) = Extract(YEAR FROM DATE(NOW()))
                AND account_move.partner_id = res_partner.commercial_partner_id
                AND account_move.company_id = ANY (array[%s])
                GROUP BY parent, bill_partner
                ORDER BY amount DESC 
            """%(company_id)
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            partner = []
            for record in docs:
                partner.append(record.get('bill_partner'))
            total_amount = []
            for record in docs:
                total_amount.append(record.get('amount'))
            result = [total_amount, partner]
        except Exception as e:
            result = []
        return result

    @api.model
    def get_customer_invoices(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT DISTINCT c.name AS partner_name,c.id AS partner_id,sum(am.amount_total) AS total
                FROM account_move am, res_partner c
                WHERE c.id = am.partner_id AND am.amount_total > 0
                AND c.customer_rank >= 1
                AND am.company_id = ANY (array[%s])
                AND am.move_type= 'out_invoice'
                GROUP BY c.name,c.id ORDER BY sum(am.amount_total) DESC LIMIT 5
            """%(company_id)
            label = ''
            self.env.cr.execute(query)
            docs = self._cr.dictfetchall()
            order = []
            for record in docs:
                order.append(record.get('total'))
            today = []
            for record in docs:
                today.append(record.get('partner_name'))
            partner_ids = [record.get('partner_id') for record in docs]
            result = [order, today, label,partner_ids]
            # return final
        except Exception as e:
            result = []
        return result

    @api.model
    def get_supplier_invoices(self):
        company_id = self._context.get('allowed_company_ids')
        supplier_result = []
        try:
            query = """
                SELECT DISTINCT c.name AS partner_name,c.id AS partner_id,sum(am.amount_total) AS total
                FROM account_move am, res_partner c
                WHERE c.id = am.partner_id AND am.amount_total > 0
                AND c.supplier_rank >= 1
                AND am.move_type= 'in_invoice'
                AND am.company_id = ANY (array[%s])
                GROUP BY c.name,c.id ORDER BY sum(am.amount_total) DESC LIMIT 5
            """%(company_id)
            label = ''
            self.env.cr.execute(query)
            docs = self._cr.dictfetchall()
            order = []
            for record in docs:
                order.append(record.get('total'))
            today = []
            for record in docs:
                today.append(record.get('partner_name'))
            partner_ids = [record.get('partner_id') for record in docs]
            supplier_result = [order, today, label,partner_ids]
        except Exception as e:
            supplier_result = []
        return supplier_result


class AccountPayment(models.Model):

    _inherit = 'account.payment'

    @api.model
    def get_customer_payment(self):
        customer_payment = self.env['account.payment'].search_count([('partner_type', '=', 'customer')])
        return customer_payment

    @api.model
    def get_vendor_payment(self):
        vendor_payment = self.env['account.payment'].search_count([('partner_type', '=', 'supplier')])
        return vendor_payment

    @api.model
    def get_customer_payment_graph(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT DISTINCT partner.name AS partner_name,partner.id AS partner_id,sum(ap.amount) AS payment_total
                FROM res_partner partner, account_payment ap
                INNER JOIN account_move am ON (ap.move_id = am.id) WHERE am.company_id = ANY (array[%s])
                AND partner.id = ap.partner_id AND ap.amount > 0
                AND partner.customer_rank >= 1
                AND ap.partner_type= 'customer'
                GROUP BY partner.name,partner.id ORDER BY sum(ap.amount) DESC LIMIT 5
            """%(company_id)
            label = ''
            self.env.cr.execute(query)
            docs = self._cr.dictfetchall()
            order = []
            for record in docs:
                order.append(record.get('payment_total'))
            today = []
            for record in docs:
                today.append(record.get('partner_name'))
            partner_ids = [record.get('partner_id') for record in docs]
            result = [order, today, label,partner_ids]
            # return final
        except Exception as e:
            result = []
        return result


class AccountJournal(models.Model):

    _inherit = 'account.journal'

    @api.model
    def get_all_journals(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT aj.name AS journal_name, aj.type AS journal_type
                FROM account_journal aj WHERE aj.company_id = ANY (array[%s])
            """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def get_all_journal_type_for_graph(self):
        company_id = self._context.get('allowed_company_ids')
        try:
            query = """
                SELECT DISTINCT aj.type AS journal_type
                FROM account_journal aj where aj.company_id = ANY (array[%s])
            """%(company_id)
            self.env.cr.execute(query)
            result = [line.get('journal_type') for line in self.env.cr.dictfetchall()]
        except Exception as e:
            result = []
        return result

class AccountMoveLine(models.Model):

    _inherit = 'account.move.line'

    @api.model
    def get_cash_bank_balance_graph(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT DISTINCT partner.name AS partner_name,partner.id AS partner_id,sum(aml.credit) AS credit_data
                FROM account_move_line aml, res_partner partner
                WHERE partner.id = aml.partner_id AND aml.credit > 0 AND aml.company_id = ANY (array[%s])
                GROUP BY partner.name,partner.id ORDER BY sum(aml.credit) DESC LIMIT 5
            """%(company_id)
            label = ''
            self.env.cr.execute(query)
            docs = self._cr.dictfetchall()
            order = []
            for record in docs:
                order.append(record.get('credit_data'))
            today = []
            for record in docs:
                today.append(record.get('partner_name'))
            partner_ids = [record.get('partner_id') for record in docs]
            result = [order, today, label,partner_ids]
        except Exception as e:
            result = []
        return result

    @api.model
    def get_income_expense(self):
        company_id = self.env.company.id
        month_list = []
        for i in range(11, -1, -1):
            l_month = datetime.now() - relativedelta(months=i)
            text = format(l_month, '%B')
            month_list.append(text)

        self._cr.execute(('''select sum(debit)-sum(credit) as income,to_char(account_move_line.date, 'Month')  as month, internal_group 
                             from account_move_line ,account_account 
                             where account_move_line.account_id=account_account.id AND internal_group = 'income' 
                             AND to_char(DATE(NOW()), 'YY') = to_char(account_move_line.date, 'YY')
                             AND parent_state = 'posted'
                             AND account_move_line.company_id = ''' + str(company_id) + '''
                             group by internal_group,month'''))
        record = self._cr.dictfetchall()

        self._cr.execute(('''select sum(debit)-sum(credit) as expense ,to_char(account_move_line.date, 'Month')  as month ,internal_group 
                            from account_move_line ,account_account 
                            where account_move_line.account_id=account_account.id AND internal_group = 'expense' 
                            AND to_char(DATE(NOW()), 'YY') = to_char(account_move_line.date, 'YY')
                            AND parent_state = 'posted'                            
                            AND account_move_line.company_id = ''' + str(company_id) + ''' 
                            group by internal_group,month'''))

        result = self._cr.dictfetchall()
        records = []
        for month in month_list:
            last_month_inc = list(filter(lambda m: m['month'].strip() == month, record))
            last_month_exp = list(filter(lambda m: m['month'].strip() == month, result))
            if not last_month_inc and not last_month_exp:
                records.append({
                    'month': month,
                    'income': 0.0,
                    'expense': 0.0,
                    'profit': 0.0,
                })
            elif (not last_month_inc) and last_month_exp:
                last_month_exp[0].update({
                    'income': 0.0,
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_exp[0].update({
                    'profit': last_month_exp[0]['income'] - last_month_exp[0]['expense']
                })
                records.append(last_month_exp[0])
            elif (not last_month_exp) and last_month_inc:
                last_month_inc[0].update({
                    'expense': 0.0,
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
            else:
                last_month_inc[0].update({
                    'income': -1 * last_month_inc[0]['income'] if last_month_inc[0]['income'] < 1 else
                    last_month_inc[0]['income'],
                    'expense': -1 * last_month_exp[0]['expense'] if last_month_exp[0]['expense'] < 1 else
                    last_month_exp[0]['expense']
                })
                last_month_inc[0].update({
                    'profit': last_month_inc[0]['income'] - last_month_inc[0]['expense']
                })
                records.append(last_month_inc[0])
        income = []
        expense = []
        month = []
        profit = []
        for rec in records:
            income.append(rec['income'])
            expense.append(rec['expense'])
            month.append(rec['month'])
            profit.append(rec['profit'])
        return {
            'income': income,
            'expense': expense,
            'month': month,
            'profit': profit,
        }
