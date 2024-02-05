# -*- coding: utf-8 -*-
{
    'name': 'Captivea Accounting',
    'category': 'Accounting',
    'version': '1.0.1',
    'author' : 'Captivea',
    'support': 'captivea.com',
    'website': 'https://www.captivea.com',
    'license': 'OPL-1',
    'summary': """Customize Profit & Loss and Balance Sheet reports""",
    'description': """Customize Profit & Loss and Balance Sheet reports""",
    'depends': ['base', 'account_accountant','account_reports'],
    'data': [
        'data/profit_and_loss.xml',
        'data/balance_sheet.xml',
    ],
    'installable': True,
    
}
