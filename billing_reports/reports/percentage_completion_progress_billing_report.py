# -*- encoding: utf-8 -*-
import io
import base64
import xlsxwriter
from odoo import models


class PercentageCompletionProgressBillingReportXlsx(models.AbstractModel):
    _name = "percentage.completion.progress.billing.report"
    _description = "Percentage Completion Progress Billing Report"

    def _generate_report_data(self, start_date, end_date):
        """
            @private - Get data for percentage completion progress billing report
        """
        bills = self.env['account.move'].search([('move_type', '=', 'in_invoice'), ('x_studio_related_so', '!=', False), ('invoice_date', '>=', start_date), ('invoice_date', '<=', end_date)], order='invoice_date asc')
        data = []
        for bill in bills:
            total_budget_cost = round(bill.x_studio_related_so.amount_untaxed - bill.x_studio_related_so.margin)
            associated_revenue = round(bill.amount_total/total_budget_cost)
            rec = {'bill_no': bill.name,
                   'bill_date': bill.invoice_date,
                   'bill_amount': bill.amount_total,
                   'project': bill.x_studio_related_so.name,
                   'total_budget_cost': total_budget_cost,
                   'contract_amount': bill.amount_total,
                   'associated_revenue': associated_revenue,
                   }
            data.append(rec)

        return data

    def _write_report_title(self, sheet, start_date, end_date, format_subtitle):
        """
            @private - write title for the report
        """
        sheet.merge_range('B2:C2', 'Percentage Completion Progress Billing Report', format_subtitle)
        sheet.merge_range('B3:C3', f'Date : {start_date} to {end_date}', format_subtitle)

    def _generate_report(self, start_date, end_date):
        """
        @private - Generate data for progress percentage completion billing reports
        """
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()
        sheet.freeze_panes(6, 3)

        # styling
        format_header = workbook.add_format({'font_size': 10, 'bold': True, 'border': 1, 'align': 'center', 'fg_color': '#ACE2E1', 'valign': 'vcenter'})
        format_left = workbook.add_format({'border': 1, 'valign': 'vcenter', 'align': 'left'})
        format_currency = workbook.add_format({'border': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        format_currency_red = workbook.add_format({'border': 1, 'valign': 'vcenter', 'align': 'right', 'num_format': '#,##0.00'})
        format_title = workbook.add_format({'align': 'center', 'fg_color': '#ACE2E1', 'bold': 1})
        self._write_headers(sheet, format_header)
        self._write_report_title(sheet, start_date, end_date, format_title)

        # generate report data
        progress_billing_data = self._generate_report_data(start_date, end_date)
        j = 6
        revenue_total = 0
        # write table body
        for line in progress_billing_data:
            sheet.write(j, 1, line['bill_no'] or '', format_left)
            sheet.set_column(1, 1, 10)
            sheet.write(j, 2, str(line['bill_date']) or '', format_left)
            sheet.set_column(2, 2, 40)
            sheet.write(j, 3, line["bill_amount"] if line['bill_amount'] != 0 else '' or '', format_currency)
            sheet.set_column(3, 3, 12)
            sheet.write(j, 4, line["project"], format_left)
            sheet.write(j, 5, line["total_budget_cost"], format_currency)
            sheet.write(j, 6, line["contract_amount"], format_currency)
            sheet.write(j, 7, line["associated_revenue"], format_currency)
            revenue_total += 0 if line['associated_revenue'] == '' else line['associated_revenue']
            j += 1
        sheet.merge_range(j, 5, j, 6, 'Total', format_title)
        sheet.write(j, 7, f'{round(revenue_total, 2):,}', format_currency)
        workbook.close()
        # generating name and encoding xlsx file
        file = base64.encodebytes(output.getvalue())
        report_name = f'Percentage Completion Progress Billing Report - {start_date} to {end_date}'
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

        # Headings for the table
        sheet.merge_range('B5:B6', 'VENDOR BILL NUMBER', format_header)
        sheet.merge_range('C5:C6', 'BILL DATE', format_header)
        sheet.merge_range('D5:D6', 'VENDOR BILL AMOUNT', format_header)
        sheet.merge_range('E5:E6', 'PROJECT #', format_header)
        sheet.merge_range('F5:F6', 'TOTAL BUDGETED COSTS', format_header)
        sheet.merge_range('G5:G6', 'CONTRACT AMOUNT', format_header)
        sheet.merge_range('H5:H6', 'ASSOCIATED REVENUE', format_header)