# -*- encoding: utf-8 -*-
{
    "name": "Billing Reports",
    "summary": "This module allows users to generate the billing reports",
    "description": """
            This module allows users to generate the billing reports
    """,
    "version": "1.0.7",
    "category": "Accounting",
    "author": "Ranga Dharmapriya",
    "support": "rangadharmapriya@gmail.com",
    "depends": ['account', 'sale', 'project', 'purchase', 'account_reports'],
    "data": [
        'security/ir.model.access.csv',
        'wizard/progress_billing_wizard_views.xml',
        'wizard/percentage_completion_progress_billing_wizard_views.xml'
    ],
    "installable": True,
    "license": "OPL-1",
}
