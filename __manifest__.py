# -*- coding: utf-8 -*-
{
    'name': "natacio",

    'summary': "Gestio de clubs, nadadors i campionats de natacio",

    'description': """
Mòdul per gestionar clubs, categories, nadadors, estils, campionats, sessions i proves de natacio.
    """,

    'author': "Ruben",
    'website': "https://www.yourcompany.com",

    'category': 'Sports',
    'version': '1.0',

    'depends': ['base'],

    'data': [

        "security/ir.model.access.csv",
        "views/views.xml",
    ],

    'demo': [
    'demo/demo.xml',
],

    'installable': True,
    'application': True,
}
