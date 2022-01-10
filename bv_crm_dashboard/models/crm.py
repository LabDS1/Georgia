from odoo import models, fields, api, _
from odoo.http import request
import datetime
from odoo.exceptions import ValidationError, UserError


class Team(models.Model):
    _inherit = 'crm.team.member'

    sales_target_line = fields.One2many('sales.target', 'crm_team_member_id', string='Sales Target')


class SalesTarget(models.Model):
    _name = 'sales.target'
    _description = 'Sales Target Management'

    def _compute_target_achieved_amount(self):
        all_total = 0
        team_member_id = self._context.get('sales_person_id')
        for rec in self:
            from_date = rec.date_from
            to_date = rec.date_to
            # if to_date <= from_date:
            #     raise UserError(_("Sorry, 'Date To' Must be greater Than 'Date From'..."))
            # target_invoice_ids = self.env['account.move'].sudo().search([
            #     ('invoice_user_id', '=', team_member_id),
            #     ('payment_state', 'in', ('paid', 'in_payment')),
            #     ('state', '=', 'posted'),
            #     ('move_type', '=', 'out_invoice'),
            #     ('invoice_date', '>=', from_date),
            #     ('invoice_date', '<=', to_date)
            # ])
            target_sale_ids = self.env['sale.order'].sudo().search([
                ('user_id', '=', team_member_id),
                ('state', 'in', ('sale', 'done')),
                ('date_order', '>=', from_date),
                ('date_order', '<=', to_date)
            ])
            # print("====@@@==>", target_sale_ids)

            if len(target_sale_ids) > 0:
                for total in target_sale_ids:
                    all_total += total.amount_total
                    rec.target_achieved_amount = all_total
                    rec.write({'target_achieved_amount_hidden': all_total})
            else:
                rec.target_achieved_amount = all_total
                rec.write({'target_achieved_amount_hidden': all_total})
            all_total = 0

    crm_team_member_id = fields.Many2one('crm.team.member', string='Team member')
    date_from = fields.Date(string='Date From', required=True)
    date_to = fields.Date(string='Date To', required=True)
    target_amount = fields.Float(string='Target Amount')
    target_achieved_amount = fields.Float(string='Target Achieved', compute='_compute_target_achieved_amount') #
    target_achieved_amount_hidden = fields.Float()


class Lead(models.Model):
    _inherit = 'crm.lead'

    @api.model
    def get_my_pipeline(self):
        
        uid = request.session.uid
        company_id = self._context.get('allowed_company_ids')
        # user_id=self.env['res.users'].browse(uid)

        if self.env.user.has_group('base.group_user') and self.env.is_admin():
            domain = [('stage_id', 'in', ['Needs Analysis', 'Quotation Sent']), ('company_id', 'in', company_id)]
            user_id = ""
        else:
            domain = [('user_id', '=', uid), ('stage_id', 'in', ['Needs Analysis', 'Quotation Sent']), ('company_id', 'in', company_id)]
            user_id = 'user_id =' + str(uid) + "AND"

        my_pipeline = self.env['crm.lead'].sudo().search_count(domain)
        query = """
                SELECT sum(cl.expected_revenue) AS expected_revenue 
                FROM crm_lead cl
                WHERE """+user_id+""" cl.company_id = ANY (array[%s]) AND active='true'
                AND stage_id IN (SELECT id from crm_stage WHERE name IN ('Needs Analysis', 'Quotation Sent')) 
                """ % (company_id)
        self.env.cr.execute(query)
        result = self.env.cr.dictfetchall()
        return my_pipeline, result

    @api.model
    def get_total_lead_opportunity(self):
        uid = request.session.uid
        # print("=====>>>>>>>@@@@@", self.env.user.groups_id)
        if self.env.user.has_group('base.group_user') and self.env.is_admin():
            domain = ['|', ('type', '=', 'lead'), ('type', '=', False)]
        else:
            domain = ['|', ('type', '=', 'lead'), ('type', '=', False), ('user_id', '=', uid)]

        total_leads_opportunities = self.env['crm.lead'].sudo().search_count(domain)
        return total_leads_opportunities

    @api.model
    def get_open_opportunity(self):
        uid = request.session.uid
        if self.env.user.has_group('base.group_user') and self.env.is_admin():
            domain = [('type', '=', 'opportunity'), ('probability', '<', 100), ('company_id', 'in', self._context.get('allowed_company_ids')), ('stage_id', 'in', ['Quotation Sent'])]
        else:
            domain = [('user_id', '=', uid), ('type', '=', 'opportunity'), ('probability', '<', 100), ('company_id', 'in', self._context.get('allowed_company_ids')), ('stage_id', 'in', ['Quotation Sent'])]

        total_open_opportunities=self.env['crm.lead'].sudo().search_count(domain)
        return total_open_opportunities

    @api.model
    def get_overdue_opportunity(self):
        today_date = datetime.datetime.now().date()

        uid = request.session.uid
        if self.env.user.has_group('base.group_user') and self.env.is_admin():
            domain = [('type', '=', 'opportunity'), ('date_deadline', '<', today_date), ('date_closed', '=', False), ('company_id', 'in', self._context.get('allowed_company_ids'))]
        else:
            domain = [('user_id', '=', uid), ('type', '=', 'opportunity'), ('date_deadline', '<', today_date), ('date_closed', '=', False), ('company_id', 'in', self._context.get('allowed_company_ids'))]

        total_overdue_opportunities = self.env['crm.lead'].sudo().search_count(domain)
        return total_overdue_opportunities

    @api.model
    def get_total_won(self):
        uid = request.session.uid
        if self.env.user.has_group('base.group_user') and self.env.is_admin():
            domain = [('active', '=', True), ('probability', '=', 100), ('company_id', 'in', self._context.get('allowed_company_ids'))]
        else:
            domain = [('user_id', '=', uid), ('active', '=', True), ('probability', '=', 100), ('company_id', 'in', self._context.get('allowed_company_ids'))]

        total_won = self.env['crm.lead'].sudo().search_count(domain)
        return total_won

    @api.model
    def get_total_loss(self):
        uid = request.session.uid
        if self.env.user.has_group('base.group_user') and self.env.is_admin():
            domain = [('active', '=', False), ('probability', '=', 0), ('company_id', 'in', self._context.get('allowed_company_ids'))]
        else:
            domain = [('user_id', '=', uid), ('active', '=', False), ('probability', '=', 0), ('company_id', 'in', self._context.get('allowed_company_ids'))]

        total_loss = self.env['crm.lead'].sudo().search_count(domain)
        return total_loss

    # @api.model
    # def get_to_be_invoiced(self):
    #     to_be_invoiced = self.env['sale.order'].search_count([('invoice_status','=','to invoice'), ('company_id', 'in', self._context.get('allowed_company_ids'))])
    #     return to_be_invoiced

    @api.model
    def get_total_archived(self):

        uid = request.session.uid
        if self.env.user.has_group('base.group_user') and self.env.is_admin():
            domain = [('active', '=', False), ('company_id', 'in', self._context.get('allowed_company_ids'))]
        else:
            domain = [('user_id', '=', uid), ('active', '=', False), ('company_id', 'in', self._context.get('allowed_company_ids'))]

        total_archived = self.env['crm.lead'].search_count(domain)
        return total_archived

    @api.model
    def get_expected_revenue(self):
        uid = request.session.uid
        if self.env.user.has_group('base.group_user') and self.env.is_admin():
            domain = [('company_id', 'in', self._context.get('allowed_company_ids')), ('priority', 'in', ('2', '3')), ('stage_id.name', '=', 'Quotation Sent')]
        else:
            domain = [('user_id', '=', uid), ('company_id', 'in', self._context.get('allowed_company_ids')), ('priority', 'in', ('2', '3')), ('stage_id.name', '=', 'Quotation Sent')]

        obj_opr=self.env['crm.lead'].sudo().search(domain)
        expected_revenue=0
        for lead in obj_opr:
            expected_revenue=round(expected_revenue + (lead.expected_revenue or 0.0) * (lead.probability or 0) / 100.0, 2)
        return expected_revenue

    @api.model
    def get_lead_opportunity(self):
        company_id = self._context.get('allowed_company_ids')
        uid = request.session.uid
        if self.env.user.has_group('base.group_user') and self.env.is_admin():
            user_id = ""
        else:
            user_id = 'AND cl.user_id =' + str(uid)
        result = []
        try:
            query = """
                SELECT cl.name AS cl_name, cl.expected_revenue AS cl_revenue, cl.probability AS cl_probability, cl.create_date AS cl_date, cl.id AS lead_id
                FROM crm_lead cl
                WHERE cl.probability > 0 AND cl.expected_revenue > 0 AND cl.probability < 100  """ + user_id + """ AND cl.company_id = ANY (array[%s]) 
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
        uid = request.session.uid
        if self.env.user.has_group('base.group_user') and self.env.is_admin():
            user_id = ""
        else:
            user_id = 'AND cl.user_id =' + str(uid)
        result = []
        try:
            query = """
                SELECT cl.name AS cl_name, cl.probability AS cl_probability, cl.create_date AS cl_date, cl.id AS cl_id
                FROM crm_lead cl
                WHERE cl.probability = 100 """ + user_id + """ AND cl.company_id = ANY (array[%s])
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
        uid = request.session.uid
        if self.env.user.has_group('base.group_user') and self.env.is_admin():
            user_id = ""
        else:
            user_id = 'AND cl.user_id =' + str(uid)
        result = []
        try:
            query = """
                SELECT cl.name AS cl_name, cl.probability AS cl_probability, cl.create_date as cl_date, cl.id AS cl_id
                FROM crm_lead cl
                WHERE cl.probability = 0 """ + user_id + """ AND cl.company_id = ANY (array[%s])
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

        uid = request.session.uid
        if self.env.user.has_group('base.group_user') and self.env.is_admin():
            user_id = ""
        else:
            user_id = 'AND cl.user_id =' + str(uid)

        try:
            query = """
                SELECT DISTINCT c.name AS partner_name, sum(cl.expected_revenue) AS cl_plan_revenue, c.id AS customer_id
                FROM crm_lead cl, res_partner c
                WHERE c.id = cl.partner_id AND cl.expected_revenue > 0 """ + user_id + """ AND cl.company_id = ANY (array[%s])
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
            query = """ 
                        SELECT DISTINCT to_char(lead.create_date, 'YYYY-MM') AS dates, SUM(lead.expected_revenue) AS revenue, to_char(lead.create_date, 'YYYY-MON') AS yr_mon
                        FROM crm_lead lead, crm_stage ct
                        WHERE lead.priority IN ('2','3') 
                        AND ct.id = lead.stage_id 
                        AND ct.name='Quotation Sent' 
                        AND lead.active=TRUE 
                        AND lead.company_id = ANY (array[%s])
                        GROUP BY dates, ct.id, yr_mon
                        ORDER BY dates DESC
                    """ % (company_id)
            self._cr.execute(query)
            docs = self._cr.dictfetchall()
            date = []
            for record in docs:
                date.append(record.get('dates'))
            revenue = []
            for record in docs:
                revenue.append(record.get('revenue'))
            yr_mon = [record.get('yr_mon') for record in docs]
            result = [revenue, date, yr_mon]
            # print("===>", result)
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

    @api.model
    def get_target_vs_achieved(self):
        company_id = self._context.get('allowed_company_ids')
        result = []
        data = []
        try:
            query = """
                SELECT DISTINCT st.id AS st_id,st.date_from AS date_from, st.date_to AS date_to, 
                st.target_achieved_amount_hidden AS achieved_amount, st.target_amount AS target_amount,
                ru.id AS res_user_id, rp.name AS rp_name, extract(year from st.date_from) AS Year
                FROM sales_target st, crm_team_member ctm, res_users AS ru, res_partner AS rp 
                WHERE st.crm_team_member_id = ctm.id AND ctm.user_id = ru.id AND rp.id = ru.partner_id AND ru.company_id = ANY (array[%s]) 
                GROUP BY st_id, date_from, date_to, res_user_id, achieved_amount, rp_name 
                ORDER BY date_from, year DESC
            """%(company_id)
            self._cr.execute(query)
            docs = self.env.cr.dictfetchall()
            year_list = list(set([record.get('year') for record in docs]))
            year_list.sort(reverse=True)
            id_list = list(set([record.get('res_user_id') for record in docs]))
            for year in year_list:
                for res_id in id_list:
                    count = 0
                    yearly_achieved = 0
                    yearly_target = 0
                    record_dict = {}
                    for record in docs:
                        if record.get('res_user_id') == res_id and record.get('year') == year:
                            record_dict['year'] = year
                            record_dict['res_user_id'] = res_id
                            # count += 1
                            month_day = str(record['date_from'].month)+'-'+str(record['date_from'].day)
                            if month_day == '1-1':
                                count = 1
                            if month_day == '4-1':
                                count = 2
                            if month_day == '7-1':
                                count = 3
                            if month_day == '10-1':
                                count = 4
                            record_dict['sales_person_name'] = record.get('rp_name')
                            record_dict['q'+str(count)+'_achieved_amount'] = round(record.get('achieved_amount'), 2)
                            yearly_achieved += record.get('achieved_amount')
                            record_dict['q'+str(count)+'_target_amount'] = round(record.get('target_amount'), 2)
                            yearly_target += record.get('target_amount')

                            record_dict['yearly_achieved_total'] = round(yearly_achieved, 2)
                            record_dict['yearly_target_total'] = round(yearly_target, 2)
                    data.append(record_dict)
            result = list(filter(None, data))
        except Exception as e:
            result = []
        return result
