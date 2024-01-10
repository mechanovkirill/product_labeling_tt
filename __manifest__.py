# -*- coding: utf-8 -*-
{
    'name': "Product labeling",
    'category': 'Sales',
    'version': '17.0',
    'sequence': 1,
    'description': """
    """,
    'depends': ['base', 'contacts'],
    'data': [
        'security/ir.model.access.csv',
        'data/data.xml',
        'views/lp_product_views.xml',
        'views/labeled_product_views.xml',
        'views/lp_warehouse_views.xml',
        'views/pl_act_views.xml',
        'views/pl_move_views.xml',
        'views/lp_operation_type_views.xml',
        'views/menus.xml',
    ],
    # only loaded in demonstration mode
    'demo': [
    ],
    'images': [
    ],
    'author': 'Mechanov Kirill',
    'installable': True,
    'application': True,
    'license': 'LGPL-3',
}