from odoo import models, fields, api

class ProjectProject(models.Model):
    _inherit = "project.project"

    vendor_bill_ids = fields.One2many(
        'account.move', 
        string="Vendor Bills", 
        compute="_compute_vendor_bill_ids"
    )

    @api.depends(
        'x_studio_sales_order',
        'x_studio_sales_order.order_line.purchase_line_ids.move_ids'
    )
    def _compute_vendor_bill_ids(self):
        for project in self:
            vendor_bills = self.env['account.move']
            sale_order = project.x_studio_sales_order

            if sale_order:
                # Fetch all purchase orders related to this sale order via x_studio_field_esSHX
                purchase_orders = self.env['purchase.order'].search([
                    ('x_studio_field_esSHX', '=', sale_order.id)
                ])

                # Collecting all vendor bills associated with these purchase orders
                for po in purchase_orders:
                    po_vendor_bills = po.invoice_ids.filtered(lambda inv: inv.move_type == 'in_invoice')
                    vendor_bills |= po_vendor_bills

            project.vendor_bill_ids = vendor_bills

    def action_view_vendor_bills(self):
        """This function returns an action that displays existing vendor bills related to the project."""
        self.ensure_one()
        vendor_bills = self.vendor_bill_ids
        result = self.env['ir.actions.act_window']._for_xml_id('account.action_move_in_invoice_type')
        
        # choose the view_mode accordingly
        if len(vendor_bills) > 1:
            result['domain'] = [('id', 'in', vendor_bills.ids)]
        elif len(vendor_bills) == 1:
            res = self.env.ref('account.view_move_form', False)
            form_view = [(res and res.id or False, 'form')]
            if 'views' in result:
                result['views'] = form_view + [(state, view) for state, view in result['views'] if view != 'form']
            else:
                result['views'] = form_view
            result['res_id'] = vendor_bills.id
        else:
            result = {'type': 'ir.actions.act_window_close'}

        return result
