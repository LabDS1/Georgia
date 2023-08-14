# -*- coding: utf-8 -*-
{
    'name': "BV Tax Cloud customaisation",
    'summary': """BV Tax Cloud customaisation""",
    'description': """BV Tax Cloud customaisationn""",
    'author': "Brainvire Infotech Inc.",
    'website': "http://www.brainvire.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['account'],
    'data': [
        'security/ir.model.access.csv',
        'views/account_tax.xml',
        'wizard/set_account_on_tax.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}
