# -*- encoding: utf-8 -*-
import io
import base64
import xlsxwriter
from odoo import models


class ProgressBillingReportXlsx(models.AbstractModel):
    _name = "progress.billing.report"
    _description = "Progress Billing Report"

    def _generate_report_data(self, start_date, end_date):
        """
            @private - Get data for progress billing report
        """
        orders = self.env['sale.order'].search_read([('analytic_account_id', '!=', False), ('create_date', '>=', start_date), ('create_date', '<=', end_date)], ['name', 'analytic_account_id', 'date_order', 'amount_untaxed', 'margin', 'invoiced_amount', 'invoice_ids'])
        data = []
        count = 0
        for so in orders:
            rec = {'pro_no': so['name'],
                   'pro_name': so['analytic_account_id'][1],
                   'date_confirmed': so['date_order'],
                   'untaxed_amount': so['amount_untaxed'],
                   'margin': so['margin'],
                   'inv_total': so['invoiced_amount'],
                   'inv_date': '',
                   'inv_no': '',
                   'inv_amount': '',
                   'bill_no': '',
                   'bill_date': '',
                   'bill_amount': '',
                   'total_budget_cost': so['amount_untaxed'] - so['margin'],
                   'complete': round((so['invoiced_amount']/so['amount_untaxed'])*100, 2) if so['amount_untaxed'] != 0 else 0,
                   'revenue': 0
                   }
            data.append(rec)
            invoices = self.env['account.move'].browse(so['invoice_ids'])
            bills = self.env['purchase.order'].search([('so_id', '=', so['id'])]).invoice_ids
            lines = invoices + bills

            if rec['complete'] >= 100:
                rec['revenue'] = so['amount_untaxed']
            else:
                rec['revenue'] = round((sum(bills.mapped('amount_total'))/rec['total_budget_cost'])*so['amount_untaxed'], 2) if so['amount_untaxed'] != 0 and rec['total_budget_cost'] != 0 else 0

            rec_count = 0
            for inv in lines:
                if rec_count == 0:
                    rec = data[count]
                    rec.update({
                        'inv_date': inv.invoice_date if inv.move_type == 'out_invoice' else '',
                        'inv_no': inv.name if inv.move_type == 'out_invoice' else '',
                        'inv_amount': inv.amount_total if inv.move_type == 'out_invoice' else '',
                        'bill_no': inv.name if inv.move_type == 'in_invoice' else '',
                        'bill_date': inv.invoice_date if inv.move_type == 'in_invoice' else '',
                        'bill_amount': inv.amount_total if inv.move_type == 'in_invoice' else ''
                    })
                    rec_count += 1
                else:
                    rec = {
                        'pro_no': '',
                        'pro_name': '',
                        'date_confirmed': '',
                        'untaxed_amount': '',
                        'margin': '',
                        'inv_total': '',
                        'total_budget_cost': '',
                        'complete': '',
                        'revenue': 0,
                        'inv_date': inv.invoice_date if inv.move_type == 'out_invoice' else '',
                        'inv_no': inv.name if inv.move_type == 'out_invoice' else '',
                        'inv_amount': inv.amount_total if inv.move_type == 'out_invoice' else '',
                        'bill_no': inv.name if inv.move_type == 'in_invoice' else '',
                        'bill_date': inv.invoice_date if inv.move_type == 'in_invoice' else '',
                        'bill_amount': inv.amount_total if inv.move_type == 'in_invoice' else ''
                    }
                    data.append(rec)
            count += 1
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

        # styling
        format_header = workbook.add_format(
            {'font_size': 10, 'bold': True, 'border': 1, 'align': 'center', 'fg_color': '#9fd3e2',
             'valign': 'vcenter'})
        format_left = workbook.add_format({'border': 1, 'valign': 'vcenter', 'align': 'left'})
        format_currency = workbook.add_format(
            {'border': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '0.00'})
        format_title = workbook.add_format({'align': 'center', 'fg_color': '#c4bd97', 'bold': 1})
        format_total = workbook.add_format(
            {'align': 'right', 'num_format': '0.00', 'fg_color': '#c4bd97', 'bold': 1})
        self._write_headers(sheet, format_header)
        self._write_report_title(sheet, start_date, end_date, format_title)

        # generate report data
        progress_billing_data = self._generate_report_data(start_date, end_date)
        j = 6
        count = 1
        total_revenue = 0
        # write table body
        for line in progress_billing_data:
            # Write values
            sheet.write(j, 1, line['pro_no'] or '', format_left)
            sheet.write(j, 2, line['pro_name'] or '', format_left)
            sheet.write(j, 3, str(line['date_confirmed']) or '', format_left)
            sheet.write(j, 4, line['untaxed_amount'], format_currency)
            sheet.write(j, 5, line['margin'], format_currency)
            sheet.write(j, 6, line['inv_total'], format_currency)
            sheet.write(j, 7, str(line['inv_date']), format_left)
            sheet.write(j, 8, line['inv_no'], format_left)
            sheet.write(j, 9, line['inv_amount'], format_currency)
            sheet.write(j, 10, line['bill_no'], format_left)
            sheet.write(j, 11, str(line['bill_date']), format_left)
            sheet.write(j, 12, line['bill_amount'], format_currency)
            sheet.write(j, 13, line['total_budget_cost'], format_currency)
            sheet.write(j, 14, line['complete'], format_left)
            sheet.write(j, 15, line['revenue'], format_currency)
            total_revenue += line['revenue']
            j += 1
            count += 1
        sheet.merge_range(j, 13, j, 14, 'Total', format_title)
        sheet.write(j, 15, total_revenue, format_total)
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

        # Headings for the table
        sheet.merge_range('B5:B6', 'PROJECT #', format_header)
        sheet.merge_range('C5:C6', 'PROJECT NAME', format_header)
        sheet.merge_range('D5:D6', 'DATE CONFIRMED', format_header)
        sheet.merge_range('E5:E6', 'CONTRACT UNTAXED AMOUNT', format_header)
        sheet.merge_range('F5:F6', 'PROJECTED MARGIN', format_header)
        sheet.merge_range('G5:G6', 'INVOICE TOTAL', format_header)
        sheet.merge_range('H5:H6', 'INVOICE DATE', format_header)
        sheet.merge_range('I5:I6', 'INVOICE NUMBER', format_header)
        sheet.merge_range('J5:J6', 'INVOICE AMOUNT', format_header)
        sheet.merge_range('K5:K6', 'VENDOR BILL NUMBER', format_header)
        sheet.merge_range('L5:L6', 'VENDOR BILL DATE', format_header)
        sheet.merge_range('M5:M6', 'VENDOR BILL AMOUNT', format_header)
        sheet.merge_range('N5:N6', 'TOTAL BUDGETED COSTS', format_header)
        sheet.merge_range('O5:O6', '% COMPLETE', format_header)
        sheet.merge_range('P5:P6', 'ASSOCIATED REVENUE', format_header)