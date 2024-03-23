# -*- encoding: utf-8 -*-
{
    "name": "Billing Reports",
    "summary": "This module allows users to generate the billing reports",
    "description": """
            This module allows users to generate the billing reports
    """,
    "version": "1.0.1",
    "category": "Accounting",
    "author": "Ranga Dharmapriya",
    "support": "rangadharmapriya@gmail.com",
    "depends": ['account', 'sale', 'project', 'purchase', 'account_reports', 'report_xlsx_helper'],
    "data": [
        'security/ir.model.access.csv',
        'wizard/progress_billing_wizard_views.xml'
    ],
    "installable": True,
    "license": "OPL-1",
}
