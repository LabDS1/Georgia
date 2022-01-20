# -*- coding: utf-8 -*-
{
    'name': "Modern CRM Dashboard",
    'summary': """Modern CRM Dashboard""",
    'description': """Modern CRM Dashboard""",
    'author': "Brainvire Infotech Inc.",
    'website': "http://www.brainvire.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['sale_management', 'sale', 'crm', 'point_of_sale', 'account', 'stock', 'purchase', 'purchase_stock','hr'],
    'data': [
        'security/dashboard_security.xml',
        'security/ir.model.access.csv',
        'views/templates.xml',
        'views/crm_team_member_views.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'bv_crm_dashboard/static/src/css/modern_dashboard.css',
            'bv_crm_dashboard/static/lib/Chart.bundle.js',
            'bv_crm_dashboard/static/lib/Chart.bundle.min.js',
            'bv_crm_dashboard/static/lib/Chart.min.js',
            'bv_crm_dashboard/static/lib/Chart.js',
            'bv_crm_dashboard/static/lib/bootstrap-toggle-master/js/bootstrap-toggle.min.js',
            'bv_crm_dashboard/static/src/js/crm_dashboard.js',
        ],
        'web.assets_qweb': [
            'bv_crm_dashboard/static/src/xml/crm_dashboard.xml',
        ],
    }
}
