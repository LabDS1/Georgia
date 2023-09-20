from odoo import models, fields, api, _
    

class ProjectProject(models.Model):
    _inherit = "project.project"

    
    so_amount_total = fields.Monetary(
        string='Total SO',
        related='sale_order_id.amount_total',
        store=True,
    )
    

    @api.model 
    def read_group(self, domain, fields, groupby, offset=0, limit=None, orderby=False, lazy=True):
        res = super(ProjectProject, self).read_group(domain, fields, groupby, offset=offset, limit=limit, orderby=orderby, lazy=lazy)
        
        for line in res:
            if '__domain' in line:
                lines = self.search(line['__domain'])
                so_amount_total = 0.0
                for record in lines:
                    so_amount_total += record.so_amount_total
                line['so_amount_total'] = so_amount_total

        return res