# -*- coding: utf-8 -*-
{
    'name': "Modern Dashboard",
    'summary': """Modern Dashboard""",
    'description': """Modern Dashboard""",
    'author': "Brainvire Infotech Inc.",
    'website': "http://www.brainvire.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['sale_management', 'sale', 'stock', 'purchase', 'purchase_stock','account'],
    'data': [
        'security/dashboard_security.xml',
        'views/templates.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,
    'assets': {
        'web.assets_backend': [
            'bv_modern_dashboard/static/src/css/modern_dashboard.css',
            'bv_modern_dashboard/static/lib/Chart.bundle.js',
            'bv_modern_dashboard/static/lib/Chart.bundle.min.js',
            'bv_modern_dashboard/static/lib/Chart.min.js',
            'bv_modern_dashboard/static/lib/Chart.js',
            'bv_modern_dashboard/static/lib/bootstrap-toggle-master/js/bootstrap-toggle.min.js',
            'bv_modern_dashboard/static/src/js/sale_dashboard.js',
            'bv_modern_dashboard/static/src/js/purchase_dashboard.js',
            'bv_modern_dashboard/static/src/js/accounting_dashboard.js',
        ],
        'web.assets_qweb': [
            'bv_modern_dashboard/static/src/xml/**/*',
        ],
    }
}
