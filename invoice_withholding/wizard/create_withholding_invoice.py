# -*- coding: utf-8 -*-

import time

from odoo import api, fields, models, _

from odoo.exceptions import UserError


class WithholdingWizLine(models.TransientModel):
    _name = "withholding.wiz.line"
    _description = "Withholding Wiz Lines"

    payment_wiz_id = fields.Many2one('withholding.payment.inv', 'Wizard')
    name = fields.Char()
    partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    project_id = fields.Many2one('project.project', 'Project')
    invoice_id = fields.Many2one('account.move', 'Invoice')
    line_id = fields.Many2one('withholding.line', 'Main WH Line')
    payment_invoice_id = fields.Many2one('account.move', 'Payment Invoice')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    amount = fields.Float(required=True)
    state = fields.Selection([
        ('to_invoice', 'To Invoiced'),
        ('invoiced', 'Invoiced')], index=True, default='to_invoice')



class WithholdingPayment(models.TransientModel):
    _name = "withholding.payment.inv"
    _description = "Withholding Payment Invoice"

    line_ids = fields.One2many('withholding.wiz.line', 'payment_wiz_id', string='Withholding Lines')
    partner_id = fields.Many2one('res.partner', 'Customer', readonly=True)

    @api.model
    def default_get(self, fields):
        res = super(WithholdingPayment, self).default_get(fields)
        vals = []
        active_model = self.env.context.get('active_model')
        active_id = self.env.context.get('active_id')
        if active_model == 'res.partner':
            domain = [('partner_id', '=', active_id), ('state','=','to_invoice')]
            res.update({'partner_id': active_id})
        if active_model == 'project.project':
            proj = self.env[active_model].browse(active_id)
            domain = [('project_id', '=', active_id), ('state','=','to_invoice')]
            res.update({'partner_id': proj.partner_id.id})
        lines = self.env['withholding.line'].search(domain)
        lines_data = []
        for line in lines:
            lines_data.append((0,0,{
                'name': line.name,
                'partner_id': line.partner_id and line.partner_id.id or False,
                'project_id': line.project_id and line.project_id.id or False,
                'invoice_id': line.invoice_id and line.invoice_id.id or False,
                'product_id': line.product_id and line.product_id.id or False,
                'payment_invoice_id': line.payment_invoice_id and line.payment_invoice_id.id or False,
                'line_id': line.id,
                'amount': line.amount,
                'state': line.state,
            }))
        res.update({'line_ids': lines_data})
        return res

    def create_invoice(self):
        inv_obj = self.env['account.move']
        inv_line_obj = self.env['account.move.line']
        invoice = inv_obj.create({
            'partner_id': self.partner_id.id,
            'move_type': 'out_invoice',
            # 'name': '-',
            'currency_id': self.env.user.company_id.currency_id.id,
            'is_withholding': True,
        })
        for line in self.line_ids:
            account_id = False
            if line.product_id:
                account_id = line.product_id.property_account_income_id.id
            if not account_id:
                prop = self.env['ir.property'].get('property_account_income_categ_id', 'product.category')
                account_id = prop and prop.id or False
            inv_line_obj.with_context(check_move_validity=False).create({
                'name': line.name,
                'price_unit': line.amount,
                'account_id': account_id,
                'quantity': 1.0,
                'discount': 0.0,
                'product_uom_id': line.product_id.uom_id.id,
                'product_id': line.product_id.id,
                'move_id': invoice.id,
                'is_withholding': True,
            })
            line.line_id.write({
                'state': 'invoiced',
                'payment_invoice_id': invoice.id
            })
            self.write({'retainage_amount': abs(line.amount_currency)})
        return invoice
    
    def create_and_view_invoice(self):
        invoice = self.create_invoice()
        action = self.env["ir.actions.actions"]._for_xml_id("account.action_move_out_invoice_type")
        action['views'] = [(self.env.ref('account.view_move_form').id, 'form')]
        action['res_id'] = invoice.id
        return action
