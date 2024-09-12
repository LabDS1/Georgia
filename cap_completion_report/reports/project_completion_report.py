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
        """
            @private - Get data for project completion report
        """
        start_date = datetime.datetime.combine(start_date, datetime.time.min)
        end_date = datetime.datetime.combine(end_date, datetime.time.max)

        # Check if the user's timezone is set, otherwise default to UTC
        user_tz = self.env.user.tz or 'UTC'
        users_tz = pytz.timezone(user_tz)

        start_date = start_date.astimezone(users_tz).date()
        end_date = end_date.astimezone(users_tz).date()

        # Filter projects by move_to_done_stage, so_amount_total, and stage
        projects = self.env['project.project'].search([
            ('move_to_done_stage', '>=', start_date),
            ('move_to_done_stage', '<=', end_date),
            ('so_amount_total', '>=', 2000),
            ('stage_id.name', '=', 'Done')  # Assuming 'Done' is the correct stage name to check
        ])

        data = []
        salesperson_groups = {}

        for project in projects:
            sales_rep = project.x_studio_sales_rep
            sale_order = project.x_studio_sales_order  # Get the linked sale order

            if sale_order:
                untaxed_amount = sale_order.amount_untaxed  # Get the amount_untaxed from the sale order
            else:
                untaxed_amount = 0

            if sales_rep not in salesperson_groups:
                salesperson_groups[sales_rep] = []

            # Fetch invoices and vendor bills related to the project
            invoices = self.env['account.move'].search([('invoice_origin', '=', project.name)])
            vendor_bills = self.env['account.move'].search([('x_studio_related_so', '=', project.id), ('move_type', '=', 'in_invoice')])

            inv_total = sum(invoices.mapped('amount_total_signed'))
            bill_total = sum(vendor_bills.mapped('amount_total'))
            actual_margin = bill_total / inv_total if inv_total else 0

            data.append({
                'sales_rep': sales_rep,
                'so_number': sale_order.name if sale_order else 'N/A',  # Use the 'x_studio_sales_order' field for SO number
                'customer': project.partner_id.name,
                'project_name': project.name,  # Use the 'name' field for the project name
                'untaxed_amount': untaxed_amount,  # Use the amount_untaxed from the sale order
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

        # Write headers
        headers = ['Sales Rep', 'SO Number', 'Customer', 'Project Name', 'Untaxed Contract Amount', 'Invoice Total', 
                   'Projected Margin', 'Vendor Bill Total', 'Actual Margin']
        header_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
        for col_num, header in enumerate(headers):
            sheet.write(0, col_num, header, header_format)  # Start headers from the 1st row

        row = 1  # Data starts from the 2nd row
        for sales_rep, orders in grouped_data.items():
            sheet.write(row, 0, sales_rep.name, header_format)  # Write the Sales Rep in the first column
            row += 1
            for order in orders:
                sheet.write(row, 1, order['so_number'])
                sheet.write(row, 2, order['customer'])
                sheet.write(row, 3, order['project_name'])
                sheet.write(row, 4, order['untaxed_amount'])
                sheet.write(row, 5, order['invoice_total'])
                sheet.write(row, 6, order['projected_margin'])
                sheet.write(row, 7, order['vendor_bill_total'])
                sheet.write(row, 8, order['actual_margin'])
                row += 1

        workbook.close()
        return output.getvalue()

    def _generate_report(self, start_date, end_date):
        grouped_data = self._generate_report_data(start_date, end_date)
        file_content = self._write_report(start_date, end_date, grouped_data)
        file_base64 = base64.b64encode(file_content)
        return file_base64, f'Project Completion Report {start_date} - {end_date}.xlsx'
