# -*- encoding: utf-8 -*-
import io
import base64
import xlsxwriter
from datetime import datetime
from calendar import monthrange

from odoo import models


class ProgressBillingReportXlsx(models.AbstractModel):
    _name = "progress.billing.report"
    _description = "Progress Billing Report"

    def get_month_start_end(self, order_date):
        year = order_date.year
        month = order_date.month
        first_day = datetime(year, month, 1)
        last_day = datetime(year, month, monthrange(year, month)[1])

        return first_day.date(), last_day.date()

    def _generate_report_data(self, start_date, end_date):
        """
            @private - Get data for progress billing report
        """
        orders = self.env['sale.order'].search_read([('analytic_account_id', '!=', False), ('state', '=', 'sale'), ('date_order', '>=', start_date), ('date_order', '<=', end_date)], ['name', 'analytic_account_id', 'date_order', 'amount_untaxed', 'amount_total', 'margin', 'invoiced_amount', 'invoice_ids'])
        data = []
        count = 0
        for so in orders:
            start = count
            main_rec = {'type': 'main', 'title': so['name']}
            data.append(main_rec)

            month_start, month_end = self.get_month_start_end(so['date_order'])

            count += 1
            complete = round(so['invoiced_amount']/so['amount_untaxed'], 2) if so['amount_untaxed'] != 0 else 0
            total_budget_cost = so['amount_untaxed'] - so['margin']
            bills = self.env['account.move'].search(
                [('move_type', '=', 'in_invoice'), ('x_studio_related_so', '=', so['id']), ('invoice_date', '>=', month_start), ('invoice_date', '<=', month_end)], order='invoice_date asc')
            rec = {'pro_no': so['name'],
                   'pro_name': so['analytic_account_id'][1],
                   'date_confirmed': so['date_order'].date(),
                   'untaxed_amount': round(so["amount_untaxed"]),
                   'total_contract_amount': round(so['amount_total']),
                   'margin': round(so["margin"]),
                   'inv_total': round(so["invoiced_amount"]),
                   'inv_date': '',
                   'inv_no': '',
                   'inv_amount': '',
                   'bill_no': '',
                   'bill_total': round(sum(bills.mapped('amount_total'))) if bills else '',
                   'bill_date': '',
                   'bill_amount': '',
                   'total_budget_cost': round(total_budget_cost, 2),
                   'complete': complete,
                   'revenue': '',
                   'total_revenue': ''
                   }
            data.append(rec)
            count += 1

            invoices = self.env['account.move'].browse(so['invoice_ids']).filtered(lambda x: x.invoice_date >= month_start and x.invoice_date <= month_end)

            inv_count = 0
            for inv in invoices:
                if inv_count == 0:
                    rec = data[count-1]
                    rec.update({
                        'inv_date': inv.invoice_date,
                        'inv_no': inv.name,
                        'inv_amount':  round(inv.amount_total_signed, 2),
                    })
                    inv_count += 1
                else:
                    rec = {
                        'pro_no': '',
                        'pro_name': '',
                        'date_confirmed': '',
                        'untaxed_amount': '',
                        'total_contract_amount': '',
                        'margin': '',
                        'inv_total': '',
                        'total_budget_cost': '',
                        'complete': '',
                        'revenue': '',
                        'total_revenue': '',
                        'inv_date': inv.invoice_date,
                        'inv_no': inv.name,
                        'inv_amount':  round(inv.amount_total_signed, 2),
                        'bill_no': '',
                        'bill_total': '',
                        'bill_date': '',
                        'bill_amount': ''
                    }
                    data.append(rec)
                    count += 1

            bill_start = start+1
            total_revenue = 0
            for bill in bills:
                revenue = round(bill.amount_total / (so['amount_total'] - so['margin']) * so['amount_total'], 2)
                total_revenue += revenue
                if bill_start < len(data):
                    rec = data[bill_start]
                    rec.update({
                        'bill_no': bill.name,
                        'bill_date': bill.invoice_date,
                        'bill_amount':  round(bill.amount_total, 2),
                        'revenue':  round(revenue, 2),
                    })
                    bill_start += 1
                else:
                    rec = {
                        'pro_no': '',
                        'pro_name': '',
                        'date_confirmed': '',
                        'untaxed_amount': '',
                        'total_contract_amount': '',
                        'margin': '',
                        'inv_total': '',
                        'total_budget_cost': '',
                        'complete': '',
                        'revenue':  round(revenue, 2),
                        'total_revenue': '',
                        'inv_date': '',
                        'inv_no': '',
                        'inv_amount': '', #(format (test_num, ',d'))
                        'bill_no': bill.name,
                        'bill_total': '',
                        'bill_date': bill.invoice_date,
                        'bill_amount': round(bill.amount_total, 2)
                    }
                    data.append(rec)
                    bill_start += 1
                    count += 1
            if total_revenue > 0:
                rec = data[start+1]
                rec.update({'total_revenue': round(total_revenue, 2)})
        return data

    def _write_report_title(self, sheet, start_date, end_date, format_subtitle):
        """
            @private - write title for the report
        """
        sheet.merge_range('B2:C2', 'Progress Billing Report', format_subtitle)
        sheet.merge_range('B3:C3', f'Date : {start_date} to {end_date}', format_subtitle)

    def _generate_report(self, start_date, end_date):
        """
        @private - Generate data for progress billing reports
        """
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        sheet.freeze_panes(6, 3)

        # styling
        format_header = workbook.add_format({'font_size': 10, 'bold': True, 'border': 1, 'align': 'center', 'fg_color': '#ACE2E1', 'valign': 'vcenter'})
        format_left = workbook.add_format({'border': 1, 'valign': 'vcenter', 'align': 'left'})
        format_currency = workbook.add_format({'border': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        percent_format = workbook.add_format({'border': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': "0%"})
        format_left_red = workbook.add_format({'border': 1, 'valign': 'vcenter', 'align': 'left', 'fg_color': '#E72929'})
        format_currency_red = workbook.add_format({'border': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        format_title = workbook.add_format({'align': 'center', 'fg_color': '#ACE2E1', 'bold': 1})
        group_format_title = workbook.add_format({'align': 'left', 'fg_color': '#41C9E2', 'bold': 1,  'border': 1})
        self._write_headers(sheet, format_header)
        self._write_report_title(sheet, start_date, end_date, format_title)

        # generate report data
        progress_billing_data = self._generate_report_data(start_date, end_date)
        j = 6
        count = 1
        revenue_total = 0
        # write table body
        for line in progress_billing_data:
            if 'type' in line:
                sheet.write(j, 1, line['title'], group_format_title)
                j += 1
            else:
                inv_total = 0 if line['inv_total'] == '' else line['inv_total']
                total_revenue = 0 if line['total_revenue'] == '' else line['total_revenue']
                sheet.write(j, 1, line['pro_no'] or '', format_left)
                sheet.set_column(1, 1, 10)
                sheet.write(j, 2, line['pro_name'] or '', format_left)
                sheet.set_column(2, 2, 40)
                sheet.write(j, 3, str(line['date_confirmed']) or '', format_left)
                sheet.set_column(3, 3, 12)
                sheet.write(j, 4, line["untaxed_amount"], format_currency) #f'{line["untaxed_amount"]:,}'
                sheet.write(j, 5, line["total_contract_amount"], format_currency) #f'{line["untaxed_amount"]:,}'
                sheet.write(j, 6, line["margin"], format_currency)
                sheet.write(j, 7, line["inv_total"], format_currency)
                sheet.write(j, 8, str(line['inv_date']), format_left)
                sheet.write(j, 9, line['inv_no'], format_left)
                sheet.write(j, 10, line["inv_amount"], format_currency)
                sheet.write(j, 11, line['bill_no'], format_left)
                sheet.write(j, 12, line['bill_total'], format_currency)
                sheet.write(j, 13, str(line['bill_date']), format_left)
                sheet.write(j, 14, line["bill_amount"] if line['bill_amount'] != 0 else '', format_currency)
                sheet.write(j, 15, line["total_budget_cost"], format_currency)
                sheet.write(j, 16, line['complete'], percent_format)
                sheet.write(j, 17, line["revenue"], format_currency)
                sheet.write(j, 18, line["total_revenue"], format_left_red if total_revenue > inv_total else format_currency)
                revenue_total += 0 if line['revenue'] == '' else line['revenue']
                j += 1
            count += 1
        sheet.merge_range(j, 13, j, 14, 'Total', format_title)
        sheet.write(j, 15, f'{round(revenue_total, 2):,}', format_currency_red)
        workbook.close()
        # generating name and encoding xlsx file
        file = base64.encodebytes(output.getvalue())
        report_name = f'Progress Billing Report - {start_date} to {end_date}'
        return file, report_name

    def _write_headers(self, sheet, format_header):
        """
        @private - Writing headers to the spreadsheet
        """
        # setting cell width
        sheet.set_column('B5:B5', 35)
        sheet.set_column('C5:C5', 15)
        sheet.set_column('D5:D5', 20)
        sheet.set_column('E5:E5', 25)
        sheet.set_column('F5:F5', 20)
        sheet.set_column('G5:G5', 30)
        sheet.set_column('H5:H5', 20)
        sheet.set_column('I5:I5', 20)
        sheet.set_column('J5:J5', 20)
        sheet.set_column('K5:K5', 20)
        sheet.set_column('L5:L5', 20)
        sheet.set_column('M5:M5', 20)
        sheet.set_column('N5:N5', 20)
        sheet.set_column('O5:O5', 20)
        sheet.set_column('O5:O5', 20)
        sheet.set_column('O5:O5', 20)
        sheet.set_column('P5:P5', 20)
        sheet.set_column('Q5:Q5', 22)
        sheet.set_column('R5:R5', 22)
        sheet.set_column('S5:S5', 22)

        # Headings for the table
        sheet.merge_range('B5:B6', 'PROJECT #', format_header)
        sheet.merge_range('C5:C6', 'PROJECT NAME', format_header)
        sheet.merge_range('D5:D6', 'DATE CONFIRMED', format_header)
        sheet.merge_range('E5:E6', 'CONTRACT UNTAXED AMOUNT', format_header)
        sheet.merge_range('F5:F6', 'TOTAL CONTRACT AMOUNT', format_header)
        sheet.merge_range('G5:G6', 'PROJECTED MARGIN', format_header)
        sheet.merge_range('H5:H6', 'INVOICE TOTAL', format_header)
        sheet.merge_range('I5:I6', 'INVOICE DATE', format_header)
        sheet.merge_range('J5:J6', 'INVOICE NUMBER', format_header)
        sheet.merge_range('K5:K6', 'INVOICE AMOUNT', format_header)
        sheet.merge_range('L5:L6', 'VENDOR BILL NUMBER', format_header)
        sheet.merge_range('M5:M6', 'VENDOR BILL TOTAL', format_header)
        sheet.merge_range('N5:N6', 'VENDOR BILL DATE', format_header)
        sheet.merge_range('O5:O6', 'VENDOR BILL AMOUNT', format_header)
        sheet.merge_range('P5:P6', 'TOTAL BUDGETED COSTS', format_header)
        sheet.merge_range('Q5:Q6', '% COMPLETE', format_header)
        sheet.merge_range('R5:R6', 'ASSOCIATED REVENUE', format_header)
        sheet.merge_range('S5:S6', 'TOTAL ASSOCIATED REVENUE', format_header)
