# -*- coding: utf-8 -*-

from odoo import fields, models, api, _
from odoo.exceptions import UserError


class WithHoldingLine(models.Model):
    _name = 'withholding.line'
    _description = "Withholding Lines"

    name = fields.Char()
    partner_id = fields.Many2one('res.partner', 'Customer', required=True)
    project_id = fields.Many2one('project.project', 'Project')
    invoice_id = fields.Many2one('account.move', 'Invoice')
    payment_invoice_id = fields.Many2one('account.move', 'Payment Invoice')
    product_id = fields.Many2one('product.product', 'Product', required=True)
    amount = fields.Float(required=True)
    state = fields.Selection([
        ('to_invoice', 'To Invoiced'),
        ('invoiced', 'Invoiced')], index=True, default='to_invoice')

    def unlink(self):
        for line in self:
            if line.state == 'invoiced':
                raise UserError(_('You can not delete a invoiced Withholding Line.'))
        return super(WithHoldingLine, self).unlink()


class ResPartner(models.Model):
    _inherit = "res.partner"

    def _withholding_count(self):
        for rec in self:
            rec.witholding_count = self.env['withholding.line'].search_count([('partner_id','=',rec.id)])

    witholding_count = fields.Integer(compute="_withholding_count", readonly=True, string="Withlodings")
    withholding_ids = fields.One2many('withholding.line', 'partner_id', string='Withholding Lines', copy=False)

    def partner_withholding_action(self):
        action = self.env["ir.actions.actions"]._for_xml_id("invoice_withholding.withholding_line_action")
        action['domain'] = [('id','in', self.withholding_ids.ids)]
        action['context'] = {'default_partner_id': self.id}
        return action


class ProjectProject(models.Model):
    _inherit = "project.project"

    def _withholding_count(self):
        for rec in self:
            rec.witholding_count = self.env['withholding.line'].search_count([('project_id','=',rec.id)])

    witholding_count = fields.Integer(compute="_withholding_count", readonly=True, string="Withlodings")
    withholding_ids = fields.One2many('withholding.line', 'project_id', string='Withholding Lines', copy=False)
    holding_percent = fields.Float('Withholding Percentage')

    def project_withholding_action(self):
        action = self.env["ir.actions.actions"]._for_xml_id("invoice_withholding.withholding_line_action")
        action['domain'] = [('id','in', self.withholding_ids.ids)]
        action['context'] = {'default_project_id': self.id}
        return action


class InvoiceMoveLine(models.Model):
    _inherit = "account.move.line"

    withholding_id = fields.Many2one('withholding.line', string='Withholding Line', copy=False)
    is_withholding = fields.Boolean(default=False)


class InvoiceMove(models.Model):
    _inherit = "account.move"

    withholding_ids = fields.One2many('withholding.line', 'invoice_id', string='Withholding Lines', copy=False)
    add_withholding = fields.Boolean("Add withholding Amount", readonly=True, states={'draft': [('readonly', False)]})
    withholding_percentage = fields.Float(string='Withholding Percentage', default=lambda self: self.env.user.company_id.withholding_percentage)
    is_withholding = fields.Boolean(default=False)
    retainage_amount = fields.Monetary()

    def action_invoice_open(self):
        res = super(InvoiceMove, self).action_invoice_open()
        lines = self.env['withholding.line'].search([('invoice_id', 'in', self.ids)])
        for line in lines:
            line.name = line.name + ' ' + line.invoice_id.number
        return res

    def _withholding_unset(self):
        if self.env.user.company_id.withholding_product_id:
            self.env['account.move.line'].search([('move_id', 'in', self.ids), ('product_id', '=', self.env.user.company_id.withholding_product_id.id)]).with_context(check_move_validity=False).unlink()
            self.env['withholding.line'].search([('invoice_id', 'in', self.ids)]).unlink()

    def create_withholding(self):
        product_id = self.env.user.company_id.withholding_product_id
        if not product_id:
            raise UserError(_('Please set Withholding product in General Settings first.'))

        # Remove Witholding line first
        self._withholding_unset()

        account_id = product_id.property_account_income_id.id
        if not account_id:
            raise UserError(_('PLease Set income account on witholding product first.'))

        for invoice in self:
            # Apply fiscal position
            taxes = product_id.taxes_id.filtered(lambda t: t.company_id.id == invoice.company_id.id)
            taxes_ids = taxes.ids
            if invoice.partner_id and self.fiscal_position_id:
                taxes_ids = self.fiscal_position_id.map_tax(taxes).ids

            amount = -(invoice.amount_total * invoice.withholding_percentage)/100

            # Create the Invoice line
            move_line = self.env['account.move.line'].with_context(check_move_validity=False).create({
                'name':  str(invoice.withholding_percentage) + '% Withholding of Invoice',
                'price_unit': amount,
                'account_id': account_id,
                'quantity': 1.0,
                'discount': 0.0,
                'product_uom_id': product_id.uom_id.id,
                'product_id': product_id.id,
                'move_id': invoice.id,
                'tax_ids': [(6, 0, taxes_ids)],
                'is_withholding': True,
            })
            self.write({'retainage_amount': abs(move_line.amount_currency)})
        self.write({'is_withholding': True})
        return True

    def action_post(self):
        res = super(InvoiceMove, self).action_post()
        WithholdingLine = self.env['withholding.line']

        for inv in self:
            if inv.add_withholding:
                for line in inv.invoice_line_ids:
                    if self.env.user.company_id.withholding_product_id and (line.product_id.id == self.env.user.company_id.withholding_product_id.id):
                        #Create witholding line
                        wh_line = WithholdingLine.create({
                            'name': line.name,
                            'product_id': line.product_id.id,
                            'partner_id': inv.partner_id.id,
                            'amount': -line.price_subtotal,
                            'invoice_id': inv.id,
                        })
                        line.with_context(check_move_validity=False).withholding_id = wh_line.id
        return res