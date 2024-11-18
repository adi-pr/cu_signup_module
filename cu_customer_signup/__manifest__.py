# -*- coding: utf-8 -*-
{
    'name': "Customer Registration",

    'summary': """Customer Registration""",

    'description': """Customer Registration""",

    'author': "Umer Daraz",
    'website': "https://www.codebyumer",

    'category': 'Website',
    'version': '17.0.0.1',
    'license': 'LGPL-3',

    # any module necessary for this one to work correctly
    'depends': ['base', 'website', 'auth_signup', 'website_sale', 'sale', 'sale_subscription'],

    # always loaded
    'data': [
        'views/signup_inherit.xml',
    ],

    'assets': {
        'web.assets_frontend': [
            'cu_customer_signup/static/src/css/style.scss',
        ],

    },

}
