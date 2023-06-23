# -*- coding: utf-8 -*-
{
    'name': "HFoc - Sale order custom",    
    'version': '15.0',
    'summary': "Sale order custom",
    'description': "Sale order custom",
    'author': "HFoc",    
    "license": "AGPL-3",
    'website' : "https://olitech.dev",
    'category': 'Localization/Base',
    'depends': ['sale'],
    'data': [        
        #'security/ir.model.access.csv',
        'views/res_config_settings.xml',
    ],
    'installable': True,
    'application': False,
    'auto_install': False,
}