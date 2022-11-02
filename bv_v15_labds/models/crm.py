from odoo import models, api, fields, _


class CrmLead(models.Model):
    _inherit = "crm.lead"

    def api_create_lead(self,vals):
        print ("valsssssssssssssssss",vals)
        msg = ""
        try:
            lead = self.env['crm.lead'].create({
                'name': vals['name'],
                'contact_name': vals['contact_name'],
                'email_from': vals['email_from'],
            })
            msg = lead.id
        except Exception as e:
            msg = "API Error: %s" % e
        return msg
