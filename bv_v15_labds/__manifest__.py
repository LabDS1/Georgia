# -*- coding: utf-8 -*-
{
    'name': "LabDS Customization",
    'summary': """LabDS Customization""",
    'description': """LabDS Customization""",
    'author': "Brainvire Infotech Inc.",
    'website': "http://www.brainvire.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['sale_management', 'sale', 'sale_margin','project','sale_timesheet','hr_timesheet', 'account_asset'],
    'data': [
        'views/sale_view.xml',
        'views/account_move_view.xml',
        'views/project_view.xml',
        'views/invoice_report_templates.xml',
        'views/project_portal_template.xml',
        'views/email_template_view.xml',
        'views/product_view.xml',
        'views/account_deferred_expense.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}
