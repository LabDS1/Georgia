# -*- encoding: utf-8 -*-
{
    "name": "CAP Project Completion Reports",
    "summary": "Module for generating project completion reports",
    "description": """
        This module allows users to generate project completion reports filtered by date and project.
    """,
    "version": "1.0.0",
    "category": "Project Management",
    "author": "Captivea",
    "depends": ['account', 'sale', 'project'],
    "data": [
        'security/ir.model.access.csv',
        'wizard/project_completion_wizard_views.xml',
        'wizard/done_date_wizard_views.xml'
    ],
    "installable": True,
    "application": False,
    "license": "OPL-1",
}