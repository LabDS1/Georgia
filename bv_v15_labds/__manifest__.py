# -*- coding: utf-8 -*-
{
    'name': "LabDS Customization",
    'summary': """LabDS Customization""",
    'description': """LabDS Customization""",
    'author': "Brainvire Infotech Inc.",
    'website': "http://www.brainvire.com",
    'category': 'Uncategorized',
    'version': '15.0.0.1',
    'depends': ['sale_management', 'sale', 'sale_margin'],
    'data': [
        'views/sale_view.xml',
        'views/account_move_view.xml',
    ],
    'installable': True,
    'auto_install': False,
    'application': True,

}
