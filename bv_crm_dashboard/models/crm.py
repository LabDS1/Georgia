from odoo import models, fields, api
from odoo.http import request
import datetime


class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def get_my_pipeline(self):
        uid = request.session.uid
        # user_id=self.env['res.users'].browse(uid)
        my_pipeline = self.env['crm.lead'].sudo().search_count([('user_id', '=', uid),
                                                                ('company_id', 'in', self._context.get('allowed_company_ids'))])
        return my_pipeline

    @api.model
    def get_total_lead_opportunity(self):
        total_leads_opportunities = self.env['crm.lead'].sudo().search_count([('company_id', 'in', self._context.get('allowed_company_ids'))])
        return total_leads_opportunities

    @api.model
    def get_open_opportunity(self):
        total_open_opportunities=self.env['crm.lead'].sudo().search_count([('type', '=', 'opportunity'),('probability', '<', 100), ('company_id', 'in', self._context.get('allowed_company_ids'))])
        return total_open_opportunities

    @api.model
    def get_overdue_opportunity(self):
        today_date = datetime.datetime.now().date()
        total_overdue_opportunities = self.env['crm.lead'].sudo().search_count([('type', '=', 'opportunity'), ('date_deadline', '<', today_date), ('date_closed', '=', False), ('company_id', 'in', self._context.get('allowed_company_ids'))])
        return total_overdue_opportunities

    @api.model
    def get_total_won(self):
        total_won = self.env['crm.lead'].sudo().search_count([('active', '=', True), ('probability', '=', 100), ('company_id', 'in', self._context.get('allowed_company_ids'))])
        return total_won

    @api.model
    def get_total_loss(self):
        total_loss = self.env['crm.lead'].sudo().search_count([('active', '=', False), ('probability', '=', 0), (
        'company_id', 'in', self._context.get('allowed_company_ids'))])
        return total_loss

    @api.model
    def get_to_be_invoiced(self):
        to_be_invoiced = self.env['sale.order'].search_count([('invoice_status','=','to invoice'), ('company_id', 'in', self._context.get('allowed_company_ids'))])
        return to_be_invoiced

    @api.model
    def get_expected_revenue(self):
        obj_opr=self.env['crm.lead'].sudo().search([('company_id', 'in', self._context.get('allowed_company_ids')), ('priority', '>=', 2), ('stage_id.name', '=', 'Quotation Sent')])
        expected_revenue=0
        for lead in obj_opr:
            expected_revenue=round(expected_revenue + (lead.expected_revenue or 0.0) * (lead.probability or 0) / 100.0, 2)
        return expected_revenue

    @api.model
    def get_lead_opportunity(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT cl.name AS cl_name, cl.expected_revenue AS cl_revenue, cl.probability AS cl_probability, cl.create_date AS cl_date, cl.id AS lead_id
                FROM crm_lead cl
                WHERE cl.probability > 0 AND cl.expected_revenue > 0 AND cl.probability < 100 AND cl.company_id = ANY (array[%s])
                ORDER BY cl.probability DESC
                """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def get_won_list(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT cl.name AS cl_name, cl.probability AS cl_probability, cl.create_date AS cl_date, cl.id AS cl_id
                FROM crm_lead cl
                WHERE cl.probability = 100 AND cl.company_id = ANY (array[%s])
                ORDER BY cl.create_date DESC
                """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def get_activity_type(self):
        result = []
        try:
            query = """
                SELECT mat.name AS activity_name, mat.id AS mat_id
                FROM mail_activity_type mat
            """
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def get_lost_list(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT cl.name AS cl_name, cl.probability AS cl_probability, cl.create_date as cl_date, cl.id AS cl_id
                FROM crm_lead cl
                WHERE cl.probability = 0 AND cl.company_id = ANY (array[%s])
                ORDER BY cl.create_date DESC
                """%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def get_partner_list(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT DISTINCT c.name AS partner_name, sum(cl.expected_revenue) AS cl_plan_revenue, c.id AS customer_id
                FROM crm_lead cl, res_partner c
                WHERE c.id = cl.partner_id AND cl.expected_revenue > 0 AND cl.company_id = ANY (array[%s])
                GROUP BY c.name, customer_id
                ORDER BY cl_plan_revenue DESC"""%(company_id)
            self.env.cr.execute(query)
            result = self.env.cr.dictfetchall()
        except Exception as e:
            result = []
        return result

    @api.model
    def get_top_salesteam_graph(self):
        result = []
        try:
            query = """
                SELECT ct.name AS sales_team_name, sum(ct.invoiced_target) AS toal_invoice_target
                FROM crm_team ct 
                WHERE ct.invoiced_target > 0 
                GROUP BY ct.name 
                """
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            sales_team = []
            for record in docs:
                sales_team.append(record.get('sales_team_name'))
            invoice_total_amount = []
            for record in docs:
                invoice_total_amount.append(record.get('toal_invoice_target'))
            result = [invoice_total_amount, sales_team]
        except Exception as e:
            result = []
        return result

    @api.model
    def get_top_sales_rep_graph(self):
        result = []
        try:
            query = """
                SELECT DISTINCT so.user_id AS sales_rep_id, sum(so.amount_total) AS total_amount, rp.name AS rep_name
                FROM sale_order so, res_users ru, res_partner as rp
                WHERE ru.id = so.user_id AND rp.id = ru.partner_id AND so.invoice_status in ('invoiced','to invoice') AND ru.active = true
                GROUP BY sales_rep_id, rep_name
                ORDER BY total_amount DESC
            """
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            sales_rep = []
            for record in docs:
                sales_rep.append(record.get('rep_name'))
            total_amount = []
            for record in docs:
                total_amount.append(record.get('total_amount'))
            sales_rep_id = [record.get('sales_rep_id') for record in docs]
            result = [total_amount, sales_rep, sales_rep_id]
        except Exception as e:
            result = []
        return result

    @api.model
    def loss_list_customer_graph(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """SELECT c.name AS partner_name, sum(cl.expected_revenue) AS cl_plan_revenue, cl.id AS cl_id
                FROM crm_lead cl, res_partner c
                WHERE cl.probability = 0 AND c.id = cl.partner_id AND cl.company_id = ANY (array[%s])
                GROUP BY c.name, cl.expected_revenue, cl.id
                ORDER BY cl.expected_revenue DESC LIMIT 5"""%(company_id)
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            partner_name = []
            for record in docs:
                partner_name.append(record.get('partner_name'))
            revenue = []
            for record in docs:
                revenue.append(record.get('cl_plan_revenue'))
            cl_id = [record.get('cl_id') for record in docs]
            result = [revenue, partner_name, cl_id]
        except Exception as e:
            result = []
        return result

    @api.model
    def total_expected_revenue_graph(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """ SELECT DISTINCT to_char(lead.create_date, 'MON-YYYY') AS date, (sum(lead.expected_revenue * lead.probability)/100) AS revenue ,to_char(lead.create_date, 'YYYY-MM') AS year
                        FROM crm_lead lead
                        WHERE lead.create_date IS NOT NULL AND lead.company_id = ANY (array[%s])
                        GROUP BY date, year
                        ORDER BY year DESC
                    """ % (company_id)
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            date = []
            for record in docs:
                date.append(record.get('date'))
            revenue = []
            for record in docs:
                revenue.append(record.get('revenue'))
            result = [revenue, date]
        except Exception as e:
            result = []
        return result

    @api.model
    def count_wise_lead(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                    SELECT count(lead.id) AS lead_name, stage.name AS stage_name, lead.stage_id AS stage_id
                    FROM crm_lead lead, crm_stage stage 
                    WHERE lead.stage_id = stage.id AND lead.company_id = ANY (array[%s])
                    GROUP BY stage_id, stage.name""" % (company_id)
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            lead = []
            for record in docs:
                lead.append(record.get('stage_name'))
            stage = []
            stage_ids = [record.get('stage_id') for record in docs]
            for record in docs:
                lead_name = self.env['crm.lead'].search_count(
                    [('stage_id', '=', record.get('stage_id')), ('company_id', 'in', company_id)])
                stage.append(lead_name)
            result = [stage, lead, stage_ids]
        except Exception as e:
            result = []
        return result

    @api.model
    def top_recent_customer(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """
                SELECT c.name AS partner_name, sum(cl.expected_revenue) AS cl_plan_revenue, c.id AS partner_id
                FROM crm_lead cl, res_partner c 
                WHERE cl.partner_id = c.id AND cl.expected_revenue > 0  AND cl.company_id = ANY (array[%s])                     
                GROUP BY c.name, cl.create_date, c.id
                ORDER BY cl.create_date DESC LIMIT 5"""%(company_id)
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            partner = []
            for record in docs:
                partner.append(record.get('partner_name'))
            lead_revenue_total = []
            for record in docs:
                lead_revenue_total.append(record.get('cl_plan_revenue'))
            partner_ids = [record.get('partner_id') for record in docs]
            result = [lead_revenue_total, partner, partner_ids]
        except Exception as e:
            result = []
        return result

    @api.model
    def won_list_customer(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        try:
            query = """SELECT c.name AS partner_name, sum(cl.expected_revenue) AS cl_plan_revenue, c.id AS partner_id
                FROM crm_lead cl, res_partner c
                WHERE cl.probability = 100 AND c.id = cl.partner_id AND cl.company_id = ANY (array[%s])
                GROUP BY c.name, cl.expected_revenue, c.id
                ORDER BY cl.expected_revenue LIMIT 5"""%(company_id)
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            partner = []
            for record in docs:
                partner.append(record.get('partner_name'))
            revenue = []
            for record in docs:
                revenue.append(record.get('cl_plan_revenue'))
            partner_ids = [record.get('partner_id') for record in docs]
            result = [revenue, partner, partner_ids]
        except Exception as e:
            result = []
        return result
