# -*- coding: utf-8 -*-
{
    'name': 'Captivea Project Invoice Withholding or Retainage Management',
    'category': 'Accounting',
    'version': '1.0.1',
    'author' : 'Captivea',
    'website': 'https://www.captivea.com',
    'license': 'OPL-1',
    'summary': """Invoice Withholding management for Projects or Retainage Management.""",
    'description': """Invoice Withholding management for Projects or Retainage Management.
    Withholding Invoice
    Withholding
    Withholding Project Management
    Withholding amount
    Retainage in invoice
    Retainage
    Retainage on project
    """,
    'depends': ['invoice_withholding','sale'],
    'data': [
        'views/withholding.xml',
    ],
    'images': [
        'static/description/icon.png',
    ],
    'installable': True,
}