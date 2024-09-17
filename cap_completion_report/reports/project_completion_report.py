import io
import pytz
import base64
import datetime
import xlsxwriter
from odoo import models

class ProjectCompletionReportXlsx(models.AbstractModel):
    _name = "project.completion.report"
    _description = "Project Completion Report"

    def _generate_report_data(self, start_date, end_date):
        start_date = datetime.datetime.combine(start_date, datetime.time.min)
        end_date = datetime.datetime.combine(end_date, datetime.time.max)

        user_tz = self.env.user.tz or 'UTC'
        users_tz = pytz.timezone(user_tz)

        start_date = start_date.astimezone(users_tz).date()
        end_date = end_date.astimezone(users_tz).date()

        projects = self.env['project.project'].search([
            ('move_to_done_stage', '>=', start_date),
            ('move_to_done_stage', '<=', end_date),
            ('so_amount_total', '>=', 2000),
            ('stage_id.name', '=', 'Done')
        ])

        data = []
        salesperson_groups = {}

        for project in projects:
            sales_rep = project.x_studio_sales_rep
            sale_order = project.x_studio_sales_order

            if sale_order:
                untaxed_amount = sale_order.amount_untaxed
                
                invoices = sale_order.invoice_ids.filtered(lambda inv: inv.state not in ['cancel'])
                inv_total = sum(invoices.mapped('amount_total_signed'))
            else:
                untaxed_amount = 0
                inv_total = 0

            if sales_rep not in salesperson_groups:
                salesperson_groups[sales_rep] = []

            vendor_bills = project.vendor_bill_ids.filtered(lambda inv: inv.move_type == 'in_invoice')
            bill_total = sum(abs(vb.amount_total_signed) for vb in vendor_bills)

            # Calculate actual margin as the difference between the invoice total and the vendor bill total
            actual_margin = inv_total - bill_total

            # Modify customer name to include company if available
            customer_name = project.partner_id.name
            if project.partner_id.parent_id:
                customer_name = f"{project.partner_id.parent_id.name}, {project.partner_id.name}"

            data.append({
                'sales_rep': sales_rep,
                'so_number': sale_order.name if sale_order else 'N/A',
                'customer': customer_name,
                'project_name': sale_order.analytic_account_id.name if sale_order.analytic_account_id else project.name,
                'untaxed_amount': untaxed_amount,
                'invoice_total': inv_total,
                'projected_margin': project.x_studio_projected_margin,
                'vendor_bill_total': bill_total,
                'actual_margin': actual_margin,
            })

        # Group by salesperson
        grouped_data = {}
        for item in data:
            sales_rep = item['sales_rep']
            if sales_rep not in grouped_data:
                grouped_data[sales_rep] = []
            grouped_data[sales_rep].append(item)

        return grouped_data

    def _write_report(self, start_date, end_date, grouped_data):
        output = io.BytesIO()
        workbook = xlsxwriter.Workbook(output, {'in_memory': True})
        sheet = workbook.add_worksheet()

        # Write Start and End Dates at the top
        date_format = workbook.add_format({'bold': True, 'align': 'left'})
        sheet.write('A1', 'Start Date', date_format)
        sheet.write('B1', str(start_date), date_format)
        sheet.write('A2', 'End Date', date_format)
        sheet.write('B2', str(end_date), date_format)

        # Write headers
        headers = ['Sales Rep', 'SO Number', 'Customer', 'Project Name', 'Untaxed Contract Amount', 'Invoice Total', 
                   'Projected Margin', 'Vendor Bill Total', 'Actual Margin']
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
        for col_num, header in enumerate(headers):
            sheet.write(3, col_num, header, header_format)  # Start headers from the 4th row

        currency_format = workbook.add_format({'num_format': '$#,##0.00'})

        row = 4  # Data starts from the 5th row
        for sales_rep, orders in grouped_data.items():
            sheet.write(row, 0, sales_rep.name, header_format)  # Write the Sales Rep in the first column
            row += 1
            for order in orders:
                sheet.write(row, 1, order['so_number'])
                sheet.write(row, 2, order['customer'])
                sheet.write(row, 3, order['project_name'])
                sheet.write(row, 4, order['untaxed_amount'], currency_format)
                sheet.write(row, 5, order['invoice_total'], currency_format)
                sheet.write(row, 6, order['projected_margin'], currency_format)
                sheet.write(row, 7, order['vendor_bill_total'], currency_format)
                sheet.write(row, 8, order['actual_margin'], currency_format)
                row += 1

        workbook.close()
        return output.getvalue()

    def _generate_report(self, start_date, end_date):
        grouped_data = self._generate_report_data(start_date, end_date)
        file_content = self._write_report(start_date, end_date, grouped_data)
        file_base64 = base64.b64encode(file_content)
        return file_base64, f'Project Completion Report {start_date} - {end_date}.xlsx'
