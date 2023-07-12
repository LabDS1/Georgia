from odoo import fields, models
from datetime import date, datetime,timedelta,timezone, time
import xlsxwriter
from xlsxwriter.utility import xl_rowcol_to_cell as rc
from odoo.exceptions import UserError
import base64
from io import BytesIO
import pytz



class QuarterlyWorkMonth(models.TransientModel):
    _name = "quarterly.work.month"
    _description = "Quarterly Work month"

    name = fields.Char(string='Sheet name', required=True)
    
    start_date = fields.Date(
        string='Start date', required=True
    )
    end_date = fields.Date(
        string='End date', required=True
    )    
    
    quarterly_work_report_id = fields.Many2one(
        string='field_name',
        comodel_name='quarterly.work.report'
    )
    
    
    

class QuarterlyWorkReport(models.TransientModel):
    _name = "quarterly.work.report"
    _description = "Quarterly Work in Progress"    

    name = fields.Char(string='/', default="Quarterly Work in Progress" )
    qwm_ids = fields.One2many(
        string='Quarterly Work months',
        comodel_name='quarterly.work.month',
        inverse_name='quarterly_work_report_id',
    )
    xls_filename = fields.Char('File name')
    xls_file = fields.Binary('FIle', readonly=True)
    

    def excel_report(self):
        for self in self:
            date=datetime.now()
            timezone = pytz.timezone(self.env.user.tz)
            date=date.astimezone(timezone).replace(tzinfo=None)
            date = date.strftime("%Y-%m-%d %H:%M:%S")
            self.write(dict(
                xls_filename='Quarterly Work %s.xlsx' % date,
                xls_file=base64.b64encode(self.process()),
            ))
            return {
                'name': 'Quarterly Work in Progress',
                'type': 'ir.actions.act_window',
                'view_type': 'form',
                'view_mode': 'form',
                'target': 'new',
                'res_model': 'quarterly.work.report',
                'res_id': self.id
            }

    def process(self):
        excel = BytesIO()
        workbook = xlsxwriter.Workbook(excel, {'in_memory': True})
        header_format_center = workbook.add_format({'valign':'bottom','bold': True, 'border':1, 'bg_color': '#C0C0C0','align': 'center'})
        header_format_center.set_text_wrap(True)

        header_format_center_2 = workbook.add_format({'valign':'bottom','bold': True, 'border':1, 'bg_color': '#CCFFFF','align': 'center'})
        header_format_center_2.set_text_wrap(True)

        header_format_center_3 = workbook.add_format({'valign':'bottom','bold': True, 'border':1, 'bg_color': '#92D050','align': 'center'})
        header_format_center_3.set_text_wrap(True)

        header_format_center_4 = workbook.add_format({'valign':'bottom','bold': True, 'border':1, 'bg_color': '#FFFF00','align': 'center'})
        header_format_center_4.set_text_wrap(True)

        num_format_red_size = workbook.add_format({'font_size':14,'bold': True,'align': 'right','border':1,'num_format': '#,##0','color': 'red'}) 
        text_left_red_size = workbook.add_format({'font_size':14,'align': 'center','bold': True,'border':1,'color': 'red'})
        
        text_left_red = workbook.add_format({'align': 'left','bold': True,'border':1,'color': 'red'})
        
        text_left = workbook.add_format({'align': 'left','bold': True,'border':1,})        
        text_left_color = workbook.add_format({'align': 'left','bold': True,'border':1,'bg_color': '#CCFFFF'})        
        num_format_color = workbook.add_format({'bold': True,'align': 'right','border':1,'num_format': '#,##0','bg_color': '#CCFFFF'}) 
        num_format_color_2 = workbook.add_format({'bold': True,'align': 'right','border':1,'num_format': '#,##0','bg_color': '#92D050'}) 
        
        num_format_color_3 = workbook.add_format({'bold': True,'align': 'right','border':1,'num_format': '#,##0','bg_color': '#FFFF00'}) 
        

        date_format = workbook.add_format({'bold': True,'align': 'right','border':1,'num_format': 'mm/d/yyyy','bg_color': '#CCFFFF'})   
        num_format = workbook.add_format({'bold': True,'align': 'right','border':1,'num_format': '#,##0'}) 
        num_format_list = workbook.add_format({'bold': True,'align': 'right','border':1,'num_format': '000000'}) 

        num_percent = workbook.add_format({'bold': True,'align': 'right','border':1,'num_format': '0%'}) 
        
        
        
        # header_format_currency = workbook.add_format({'valign':'vcenter','bold': True, 'border':1, 'bg_color': '#ddebf7','align': 'right','num_format': '#,##0.00 [$€-es-ES]'})
        

        for line in self.qwm_ids:

            sheet = workbook.add_worksheet(line.name)
            
            sheet.write(0, 0, 'PROJECT #', header_format_center)
            sheet.write(0, 1, 'PROJECT NAME', header_format_center)
            sheet.write(0, 2, 'DATE CONFIRMED', header_format_center_2)
            sheet.write(0, 3, 'SALES REP', header_format_center_2)
            sheet.write(0, 4, 'CONTRACT UNTAXED AMOUNT', header_format_center_2)
            sheet.write(0, 5, 'CUSTOMER INVOICE TO DATE', header_format_center_2)
            sheet.write(0, 6, 'PURCHASE ORDERS TO DATE', header_format_center_2)
            sheet.write(0, 7, 'TOTAL BUDGETED COSTS', header_format_center_2)
            sheet.write(0, 8, 'VENDOR BILLS', header_format_center_2)
            sheet.write(0, 9, 'VENDOR BILLS LESS INVOICE TO DATE', header_format_center_3)
            sheet.write(0, 10, 'CUSTOMER INVOICE LESS VENDOR BILLS TO DATE', header_format_center_3)
            sheet.write(0, 11, 'COST EXCEEDED', header_format_center) #Formula
            sheet.write(0, 12, 'COST SAVINGS', header_format_center_4) #Formula
            sheet.write(0, 13, 'REVIEW/NO REVIEW', header_format_center) #Formula
            sheet.write(0, 14, '% COMPLETE', header_format_center) #Formula
            sheet.write(0, 15, 'PROJECTED GROSS PROFIT', header_format_center)
            sheet.write(0, 16, '%', header_format_center)
            sheet.write(0, 17, 'GROSS PROFIT TO DATE', header_format_center)#Formula
            sheet.write(0, 18, 'OVER/UNDER BILLED', header_format_center)#Formula
            #Formula


            timezone = pytz.timezone(self.env.user.tz)
            timezone_utc = pytz.timezone('UTC')

            start_date = line.start_date
            start_date = datetime.combine(start_date, time(0,0,0))
            end_date = line.end_date
            end_date = datetime.combine(end_date, time(23,59,59))   

            start_date=timezone.localize(start_date)
            start_date=start_date.astimezone(timezone_utc).replace(tzinfo=None)
            
            end_date=timezone.localize(end_date)
            end_date=end_date.astimezone(timezone_utc).replace(tzinfo=None)

            
            sale_order_ids = self.env['sale.order'].search([
                                                ('state','in', ['sale','done']),                                                                                      
                                                ('date_order','>=',start_date),
                                                ('date_order','<=',end_date)])
            
            # raise UserError('%s - %s -- %s' % (str(start_date),str(end_date),str(sale_order_ids[0].date_order)))
            col = 0
            row = 1
            if sale_order_ids:
                for sale in sale_order_ids:

                    date_order=sale.date_order.astimezone(timezone).replace(tzinfo=None).date()        

                    invoice_ids = self.env['account.move'].search([('id','in',sale.invoice_ids.ids),('state','=', 'posted')])
                    billed_to_date = 0.00
                    if invoice_ids:
                        # billed_to_date = sum(invoice_ids.mapped('amount_total_signed'))
                        billed_to_date = sum(invoice_ids.mapped('amount_untaxed_signed'))
                        
                    vendor_bill_total = 0.00
                    # purchase_order_line_ids = self.env['purchase.order.line'].search([('sale_order_id', '=', sale.id),('state','in', ['purchase','done'])])
                    purchase_order_ids = self.env['purchase.order'].search([('x_studio_field_esSHX', '=', sale.id),('state','in', ['purchase','done'])])
                    cost_to_date = 0.00
                    if purchase_order_ids:
                        # cost_to_date = sum(purchase_order_line_ids.mapped('price_total'))
                        cost_to_date = sum(purchase_order_ids.mapped('amount_total'))
                    
                        for po in purchase_order_ids:
                            vendor_bill_total += sum(po.invoice_ids.filtered(lambda r: r.state == 'posted').mapped('amount_total')) # amount_untaxed

                    estimated_costs = sale.amount_untaxed-sale.margin

                    sheet.write(row, col, int(sale.name.replace('SO','').replace('S','').replace('O','')), num_format_list)
                    sheet.write(row, col+1, sale.analytic_account_id.name or 'None', text_left)
                    sheet.write(row, col+2, date_order , date_format)
                    sheet.write(row, col+3, sale.user_id.name or 'None' , text_left_color)
                    sheet.write(row, col+4, sale.amount_untaxed , num_format_color)
                    sheet.write(row, col+5, billed_to_date , num_format_color)
                    sheet.write(row, col+6, cost_to_date , num_format_color)
                    sheet.write(row, col+7, estimated_costs , num_format_color)
                    sheet.write(row, col+8, vendor_bill_total , num_format_color)
                    sheet.write_formula(row, col+9, '=IF(I%s-F%s<=0,"",I%s-F%s)' % (row+1,row+1,row+1,row+1) , num_format_color_2)
                    sheet.write_formula(row, col+10, '=IF(I%s=0,IF(F%s-I%s>0,F%s-I%s,""),"")' % (row+1,row+1,row+1,row+1,row+1) , num_format_color_2)
                    
                    sheet.write_formula(row, col+11, '=IF(G%s>H%s,G%s-H%s,"")' % (row+1,row+1,row+1,row+1) , num_format)#Formula
                    
                    # sheet.write_formula(row, col+12, '=IF(O%s>=1,IF(I%s<H%s,H%s-I%s,""),"")' % (row+1,row+1,row+1,row+1,row+1) , num_format_color_3)#Formula
                    sheet.write_formula(row, col+12, '=IF(AND(I%s>0,O%s>=1),IF(I%s<H%s,H%s-I%s,""),"")' % (row+1,row+1,row+1,row+1,row+1,row+1) , num_format_color_3)#Formula
                    
                    sheet.write_formula(row, col+13, '=IF(G%s>H%s,"REVIEW","")' % (row+1,row+1), text_left_red)#Formula
                    sheet.write_formula(row, col+14, '=F%s/E%s'  % (row+1,row+1) , num_percent)#Formula
                    sheet.write(row, col+15, sale.margin , num_format)
                    sheet.write(row, col+16, sale.margin_percent , num_percent)
                    sheet.write_formula(row, col+17, '=F%s-I%s' % (row+1,row+1), num_format)#Formula
                    sheet.write_formula(row, col+18, '=F%s-E%s' % (row+1,row+1), num_format)#Formula
                    
                    row += 1
            
                sheet.write(row, col, 'TOTAL', text_left_red_size)
                sheet.write(row, col+1, '' , text_left)
                sheet.write(row, col+2, '' , text_left)
                sheet.write(row, col+3, '' , text_left)
                sheet.write_formula(row, col+4, '=SUM(E2:E%s)' % str(row)  , num_format_red_size)
                sheet.write_formula(row, col+5, '=SUM(F2:F%s)' % str(row)  , num_format_red_size)
                sheet.write_formula(row, col+6, '=SUM(G2:G%s)' % str(row)  , num_format_red_size)
                sheet.write_formula(row, col+7, '=SUM(H2:H%s)' % str(row)  , num_format_red_size)
                sheet.write_formula(row, col+8, '=SUM(I2:I%s)' % str(row)  , num_format_red_size)#Formula
                sheet.write_formula(row, col+9, '=SUM(J2:J%s)' % str(row)  , num_format_red_size)
                sheet.write_formula(row, col+10, '=SUM(K2:K%s)' % str(row)  , num_format_red_size)
                sheet.write_formula(row, col+11, '=SUM(L2:L%s)' % str(row)  , num_format_red_size)#Formula
                sheet.write_formula(row, col+12, '=SUM(M2:M%s)' % str(row)  , num_format_red_size)#Formula

                sheet.write_formula(row, col+13, '=COUNTIF(N2:N%s, "REVIEW")' % str(row) , text_left_red_size)#Formula
                sheet.write(row, col+14, '' , num_percent)
                sheet.write_formula(row, col+15, '=SUM(P2:P%s)' % str(row) , num_format_red_size)
                sheet.write(row, col+16, '' , num_percent)#Formula
                sheet.write_formula(row, col+17, '=SUM(R2:R%s)' % str(row) , num_format_red_size)#Formula
                sheet.write_formula(row, col+18, '=SUM(S2:S%s)' % str(row) , num_format_red_size)#Formula
            
            sheet.set_zoom(85)
            sheet.set_row(0, 51)

            sheet.set_column(0, 0, 12)
            sheet.set_column(1, 1, 35)
            
            for i in range(2, 20):
                sheet.set_column(i, i, 12)
            
            sheet.set_column(9, 9, 16)
            sheet.set_column(10, 10, 19)
            sheet.freeze_panes(1, 2)

        workbook.close()
        excel.seek(0)
        return excel.getvalue()
