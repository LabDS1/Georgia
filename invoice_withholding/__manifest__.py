# -*- coding: utf-8 -*-
#╔══════════════════════════════════════════════════════════════════════╗
#║                                                                      ║
#║                  ╔═══╦╗       ╔╗  ╔╗     ╔═══╦═══╗                   ║
#║                  ║╔═╗║║       ║║ ╔╝╚╗    ║╔═╗║╔═╗║                   ║
#║                  ║║ ║║║╔╗╔╦╦══╣╚═╬╗╔╬╗ ╔╗║║ ╚╣╚══╗                   ║
#║                  ║╚═╝║║║╚╝╠╣╔╗║╔╗║║║║║ ║║║║ ╔╬══╗║                   ║
#║                  ║╔═╗║╚╣║║║║╚╝║║║║║╚╣╚═╝║║╚═╝║╚═╝║                   ║
#║                  ╚╝ ╚╩═╩╩╩╩╩═╗╠╝╚╝╚═╩═╗╔╝╚═══╩═══╝                   ║
#║                            ╔═╝║     ╔═╝║                             ║
#║                            ╚══╝     ╚══╝                             ║
#║                  SOFTWARE DEVELOPED AND SUPPORTED BY                 ║
#║                ALMIGHTY CONSULTING SOLUTIONS PVT. LTD.               ║
#║                      COPYRIGHT (C) 2016 - TODAY                      ║
#║                      https://www.almightycs.com                      ║
#║                                                                      ║
#╚══════════════════════════════════════════════════════════════════════╝
{
    'name': 'Project Invoice Withholding or Retainage Management',
    'category': 'Accounting',
    'version': '1.0.1',
    'author' : 'Almighty Consulting Solutions Pvt. Ltd.',
    'support': 'info@almightycs.com',
    'website': 'https://www.almightycs.com',
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
    'depends': ['account', 'project', 'account_avatax'],
    'data': [
        'security/ir.model.access.csv',
        'views/withholding_view.xml',
        'views/res_config_view.xml',
        'wizard/create_withholding_invoice_view.xml',
    ],
    'images': [
        'static/description/withholding_cover.png',
    ],
    'installable': True,
    'price': 49,
    'currency': 'EUR',
}
# vim:expandtab:smartindent:tabstop=4:softtabstop=4:shiftwidth=4: