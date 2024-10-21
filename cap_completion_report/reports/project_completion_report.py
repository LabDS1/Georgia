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
                total_contract_amount = sale_order.amount_total  # Including taxes

                invoices = sale_order.invoice_ids.filtered(lambda inv: inv.state not in ['cancel'])
                inv_total = sum(invoices.mapped('amount_total_signed'))

                # Fetch all purchase orders related to this sale order via x_studio_field_esSHX
                purchase_orders = self.env['purchase.order'].search([
                    ('x_studio_field_esSHX', '=', sale_order.id)
                ])
                issued_po_total = sum(po.amount_total for po in purchase_orders)  # Sum the total amounts of the associated purchase orders
            else:
                untaxed_amount = 0
                total_contract_amount = 0
                inv_total = 0
                issued_po_total = 0

            if sales_rep not in salesperson_groups:
                salesperson_groups[sales_rep] = []

            vendor_bills = project.vendor_bill_ids.filtered(lambda inv: inv.move_type == 'in_invoice')
            bill_total = sum(abs(vb.amount_total_signed) for vb in vendor_bills)

            actual_margin = inv_total - bill_total

            # Calculate percentages based on untaxed amount
            projected_margin_percentage = (project.x_studio_projected_margin / untaxed_amount) * 100 if untaxed_amount else 0
            actual_margin_percentage = (actual_margin / untaxed_amount) * 100 if untaxed_amount else 0

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
                'total_contract_amount': total_contract_amount,
                'invoice_total': inv_total,
                'projected_margin': project.x_studio_projected_margin,
                'vendor_bill_total': bill_total,
                'actual_margin': actual_margin,
                'projected_margin_percentage': projected_margin_percentage,
                'actual_margin_percentage': actual_margin_percentage,
                'issued_po_total': issued_po_total,  # Correctly fetching the total PO amount
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
        headers = ['Sales Rep', 'SO Number', 'Customer', 'Project Name', 'Untaxed Contract Amount', 'Total Contract Amount',
                   'Invoice Total', 'Projected Margin', 'Projected Margin %', 'Vendor Bill Total', 
                   'Actual Margin', 'Actual Margin %', 'Issued PO Total']

        header_format = workbook.add_format({'bold': True, 'align': 'center', 'border': 1})
        for col_num, header in enumerate(headers):
            sheet.write(3, col_num, header, header_format)

        currency_format = workbook.add_format({'num_format': '$#,##0.00'})
        percent_format = workbook.add_format({'num_format': '0%'})

        row = 4  # Data starts from the 5th row
        for sales_rep, orders in grouped_data.items():
            sheet.write(row, 0, sales_rep.name, header_format)
            row += 1
            for order in orders:
                sheet.write(row, 1, order['so_number'])
                sheet.write(row, 2, order['customer'])
                sheet.write(row, 3, order['project_name'])
                sheet.write(row, 4, order['untaxed_amount'], currency_format)
                sheet.write(row, 5, order['total_contract_amount'], currency_format)
                sheet.write(row, 6, order['invoice_total'], currency_format)
                sheet.write(row, 7, order['projected_margin'], currency_format)
                sheet.write(row, 8, order['projected_margin_percentage'] / 100, percent_format)
                sheet.write(row, 9, order['vendor_bill_total'], currency_format)
                sheet.write(row, 10, order['actual_margin'], currency_format)
                sheet.write(row, 11, order['actual_margin_percentage'] / 100, percent_format)
                sheet.write(row, 12, order['issued_po_total'], currency_format)  # Write the fetched PO total amount

                # Apply Conditional Formatting per row
                if order['actual_margin_percentage'] >= order['projected_margin_percentage']:
                    sheet.write(row, 11, order['actual_margin_percentage'] / 100, workbook.add_format({'bg_color': '#C6EFCE', 'font_color': '#006100', 'num_format': '0%'}))  # Green
                else:
                    sheet.write(row, 11, order['actual_margin_percentage'] / 100, workbook.add_format({'bg_color': '#FFC7CE', 'font_color': '#9C0006', 'num_format': '0%'}))  # Red

                row += 1

        # Set column widths (adjust as needed based on the expected data size)
        sheet.set_column(0, 0, 15)  # Sales Rep
        sheet.set_column(1, 1, 12)  # SO Number
        sheet.set_column(2, 2, 30)  # Customer
        sheet.set_column(3, 3, 25)  # Project Name
        sheet.set_column(4, 5, 18)  # Untaxed Contract Amount, Total Contract Amount
        sheet.set_column(6, 6, 18)  # Invoice Total
        sheet.set_column(7, 7, 18)  # Projected Margin
        sheet.set_column(8, 8, 12)  # Projected Margin %
        sheet.set_column(9, 9, 18)  # Vendor Bill Total
        sheet.set_column(10, 10, 18)  # Actual Margin
        sheet.set_column(11, 11, 12)  # Actual Margin %
        sheet.set_column(12, 12, 18)  # Issued PO Total

        workbook.close()
        return output.getvalue()

    def _generate_report(self, start_date, end_date):
        grouped_data = self._generate_report_data(start_date, end_date)
        file_content = self._write_report(start_date, end_date, grouped_data)
        file_base64 = base64.b64encode(file_content)
        return file_base64, f'Project Completion Report {start_date} - {end_date}.xlsx'
