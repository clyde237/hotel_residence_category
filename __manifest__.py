# -*- coding: utf-8 -*-
{
    'name': 'Hotel Room Availability by Category',
    'version': '18.0.1.0.0',
    'category': 'Hotel Management',
    'summary': 'Gestion de la disponibilité des appartements par catégorie',
    'description': """
        Module pour gérer et afficher la disponibilité des appartements par catégorie
        - Appartements meublés 2 chambres
        - Appartements non-meublés 2 chambres
        - Appartements meublés 3 chambres
        - Appartements non-meublés 3 chambres
    """,
    'author': 'Votre Nom',
    'website': 'https://www.votresite.com',
    'depends': [
        'base',
        'hotel_management_system',  # Module principal hotel
        'website',                   # Pour la partie site web
        'product',                   # Pour product.product
    ],
    'data': [
    'security/ir.model.access.csv',
    'data/room_categories_data.xml',
    'views/room_category_views.xml',
    'views/website_templates.xml',  # ✅ Déjà présent
    'views/snippets.xml',
    ],
    'assets': {
        'web.assets_frontend': [
            'hotel_residence_category/static/src/css/residence_categories.css',
            #'hotel_residence_category/static/src/js/residence_categories.js',
        ],
    },
    'installable': True,
    'application': False,
    'auto_install': False,
    'license': 'LGPL-3',
}