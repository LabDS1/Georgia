# -*- encoding: utf-8 -*-
import io
import pytz
import base64
import datetime
import xlsxwriter
from odoo import models


class ProgressBillingReportXlsx(models.AbstractModel):
    _inherit = "progress.billing.report"

    def _generate_report_data(self, start_date, end_date):
        """
            @private - Get data for progress billing report
        """
        start_date = datetime.datetime.combine(start_date, datetime.time.min)
        end_date = datetime.datetime.combine(end_date, datetime.time.max)

        users_tz = pytz.timezone(self.env.user.tz)

        start_date = start_date.astimezone(users_tz).date()
        end_date = end_date.astimezone(users_tz).date()

        orders = self.env['sale.order'].search_read([('analytic_account_id', '!=', False), ('state', '=', 'sale'), ('date_order', '<=', end_date)], ['name', 'analytic_account_id', 'date_order', 'amount_untaxed', 'margin', 'invoiced_amount', 'invoice_ids','withholding_ids'])

        data = []
        count = 0
        for so in orders:

            invoices = self.env['account.move'].browse(so['invoice_ids'])
            withholdings = self.env['withholding.line'].browse(so['withholding_ids'])
            filtered_invoices = invoices.filtered(lambda item: item.invoice_date and item.invoice_date <= end_date)
            check_invoices = invoices.filtered(lambda item: item.invoice_date and start_date <= item.invoice_date <= end_date)

            bills = self.env['account.move'].search(
                [('move_type', '=', 'in_invoice'), ('x_studio_related_so', '=', so['id'])], order='invoice_date asc')
            filtered_bills = bills.filtered(lambda item: item.invoice_date and item.invoice_date <= end_date)
            check_bills = bills.filtered(lambda item: item.invoice_date and start_date <= item.invoice_date <= end_date)

            if check_invoices or check_bills:
                start = count
                main_rec = {'type': 'main', 'title': so['name']}
                data.append(main_rec)
                count += 1
                inv_total = round(sum(filtered_invoices.mapped('amount_total_signed')), 2) if filtered_invoices else 0
                retainage_total = round(sum(filtered_invoices.mapped('withholding_ids').mapped('amount')), 2) if filtered_invoices else 0 
                bill_total = round(sum(filtered_bills.mapped('amount_total')), 2) if filtered_bills else 0
                total_budget_cost = so['amount_untaxed'] - so['margin']
                complete = round(bill_total/total_budget_cost, 2) if total_budget_cost != 0 else 0
                rec = {'pro_no': so['name'],
                       'pro_name': so['analytic_account_id'][1],
                       'date_confirmed': datetime.datetime.strftime(so['date_order'].date(), '%m-%d-%Y'),
                       'untaxed_amount': round(so["amount_untaxed"], 2),
                       'margin': round(so["margin"], 2),
                       'inv_total': inv_total,
                       'retainage_total': retainage_total,
                       'inv_date': '',
                       'inv_no': '',
                       'inv_amount': '',
                       'bill_no': '',
                       'bill_total': bill_total if bill_total != 0 else '',
                       'bill_date': '',
                       'bill_amount': '',
                       'total_budget_cost': round(total_budget_cost, 2),
                       'complete': complete,
                       'revenue': '',
                       'total_revenue': ''
                       }
                data.append(rec)
                count += 1

                inv_count = 0
                for inv in filtered_invoices:
                    if inv_count == 0:
                        rec = data[count-1]
                        rec.update({
                            'inv_date': datetime.datetime.strftime(inv.invoice_date, '%m-%d-%Y'),
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
                            'margin': '',
                            'inv_total': '',
                            'retainage_total': '',
                            'total_budget_cost': '',
                            'complete': '',
                            'revenue': '',
                            'total_revenue': '',
                            'inv_date': datetime.datetime.strftime(inv.invoice_date, '%m-%d-%Y'),
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
                for bill in filtered_bills:
                    revenue = round(bill.amount_total / (so['amount_untaxed'] - so['margin']) * so['amount_untaxed'], 2) if so['amount_untaxed'] != 0 else 0
                    total_revenue += revenue
                    if bill_start < len(data):
                        rec = data[bill_start]
                        rec.update({
                            'bill_no': bill.name,
                            'bill_date': datetime.datetime.strftime(bill.invoice_date, '%m-%d-%Y'),
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
                            'margin': '',
                            'inv_total': '',
                            'retainage_total': '',
                            'total_budget_cost': '',
                            'complete': '',
                            'revenue':  round(revenue, 2),
                            'total_revenue': '',
                            'inv_date': '',
                            'inv_no': '',
                            'inv_amount': '', #(format (test_num, ',d'))
                            'bill_no': bill.name,
                            'bill_total': '',
                            'bill_date': datetime.datetime.strftime(bill.invoice_date, '%m-%d-%Y'),
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
                # sheet.write(j, 1, line['title'], group_format_title)
                # j += 1
                pass
            else:
                # inv_total = 0 if line['inv_total'] == '' else line['inv_total']
                # total_revenue = 0 if line['total_revenue'] == '' else line['total_revenue']
                sheet.write(j, 1, line['pro_no'] or '', format_left)
                sheet.set_column(1, 1, 10)
                sheet.write(j, 2, line['pro_name'] or '', format_left)
                sheet.set_column(2, 2, 40)
                sheet.write(j, 3, str(line['date_confirmed']) or '', format_left)
                sheet.set_column(3, 3, 12)
                sheet.write(j, 4, line["untaxed_amount"], format_currency) #f'{line["untaxed_amount"]:,}'
                sheet.write(j, 5, line["margin"], format_currency)

                sheet.write(j, 6, line["inv_total"], format_currency)
                sheet.write(j, 7, line["retainage_total"], format_currency) # new info
                sheet.write(j, 8, str(line['inv_date']), format_left)
                sheet.write(j, 9, line['inv_no'], format_left)
                sheet.write(j, 10, line["inv_amount"], format_currency)
                # new info
                sheet.write(j, 12, line['bill_no'], format_left)
                sheet.write(j, 13, line['bill_total'], format_currency)
                sheet.write(j, 14, str(line['bill_date']), format_left)
                sheet.write(j, 15, line["bill_amount"] if line['bill_amount'] != 0 else '', format_currency)
                sheet.write(j, 16, line["total_budget_cost"], format_currency)
                sheet.write(j, 1, line['complete'], percent_format)
                # sheet.write(j, 15, line["revenue"], format_currency)
                # sheet.write(j, 16, line["total_revenue"], format_left_red if total_revenue > inv_total else format_currency)
                # revenue_total += 0 if line['revenue'] == '' else line['revenue']
                j += 1
            count += 1
        # sheet.merge_range(j, 13, j, 14, 'Total', format_title)
        # sheet.write(j, 15, f'{round(revenue_total, 2):,}', format_currency_red)
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
        sheet.set_column('H5:H5', 30) #
        sheet.set_column('I5:I5', 20)
        sheet.set_column('J5:J5', 20)
        sheet.set_column('K5:K5', 20) 
        sheet.set_column('L5:L5', 20) #
        sheet.set_column('M5:M5', 20)
        sheet.set_column('N5:N5', 20)
        sheet.set_column('O5:O5', 20)
        sheet.set_column('P5:P5', 20)
        sheet.set_column('Q5:Q5', 20)
        sheet.set_column('Q5:Q5', 20)
        # sheet.set_column('P5:P5', 20)
        # sheet.set_column('Q5:Q5', 22)

        # Headings for the table
        sheet.merge_range('B5:B6', 'PROJECT #', format_header)
        sheet.merge_range('C5:C6', 'PROJECT NAME', format_header)
        sheet.merge_range('D5:D6', 'DATE CONFIRMED', format_header)
        sheet.merge_range('E5:E6', 'CONTRACT UNTAXED AMOUNT', format_header)
        sheet.merge_range('F5:F6', 'PROJECTED MARGIN', format_header)
        sheet.merge_range('G5:G6', 'INVOICE TOTAL', format_header)
        sheet.merge_range('H5:H6', 'RETAINAGE TOTAL', format_header) #
        sheet.merge_range('I5:I6', 'INVOICE DATE', format_header)
        sheet.merge_range('J5:J6', 'INVOICE NUMBER', format_header)
        sheet.merge_range('K5:K6', 'INVOICE AMOUNT', format_header)
        sheet.merge_range('L5:L6', 'INVOICE RETAINAGE', format_header)
        sheet.merge_range('M5:M6', 'VENDOR BILL NUMBER', format_header)
        sheet.merge_range('N5:N6', 'VENDOR BILL TOTAL', format_header)
        sheet.merge_range('O5:O6', 'VENDOR BILL DATE', format_header)
        sheet.merge_range('P5:P6', 'VENDOR BILL AMOUNT', format_header)
        sheet.merge_range('Q5:Q6', 'TOTAL BUDGETED COSTS', format_header)
        sheet.merge_range('Q5:Q6', '% COMPLETE', format_header)
        # sheet.merge_range('P5:P6', 'ASSOCIATED REVENUE', format_header)
        # sheet.merge_range('Q5:Q6', 'TOTAL ASSOCIATED REVENUE', format_header)
