# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.

{
    'name': 'eCommerce sales',
    'category': 'Website/Website',
    'sequence': 51,
    'summary': 'Sell your products online with Omnisoft Solution Customization',
    'website': 'https://www.odoo.com/app/ecommerce',
    'version': '1.1',
    'depends': ['website', 'sale', 'website_payment', 'website_mail', 'website_sale', 'portal_rating', 'digest'],
    'data': [
        # Security
        'security/ir.model.access.csv',

        # Views
        'views/product_template.xml',
        'views/s_file_attachment.xml',
        'views/sale_order.xml',
        'views/web_sales_cart_summary.xml',
    ],
    'installable': True,
    'auto_install': True,
    'assets': {
        'web.assets_frontend': [
            'omni_website_sale/static/src/**/*.js',
        ],
    },
    'license': 'LGPL-3',
}
