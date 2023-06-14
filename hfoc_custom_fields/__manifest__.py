# -*- coding: utf-8 -*-
{
    'name': "HFoc - Custom Report",    
    'version': '15.0',
    'summary': "HFoc - Custom Report",
    'description': "HFoc - Custom Report",
    'author': "HFoc",    
    "license": "AGPL-3",
    'website' : "https://olitech.dev",
    'category': 'Localization/Base',
    'depends': ['sale','purchase','stock','account'],
    'data': [        
        'security/ir.model.access.csv',
        'wizard/quarterly_work_report.xml',
        'views/menus.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}