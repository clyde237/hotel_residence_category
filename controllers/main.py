# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
from odoo.addons.website_sale.controllers.main import WebsiteSale


class ResidenceCategoryController(http.Controller):

    @http.route(['/residence/categories'], type='http', auth='public', website=True, sitemap=True)
    def residence_categories(self, **kwargs):
        """
        Page d'accueil des catégories de résidence
        Affiche les 4 catégories d'appartements avec leur disponibilité
        """
        # Récupérer toutes les catégories actives
        categories = request.env['hotel.room.category'].sudo().search([
            ('active', '=', True)
        ], order='sequence, name')

        values = {
            'categories': categories,
            'page_name': 'residence_categories',
        }

        return request.render('hotel_room_availability.residence_categories_page', values)

    @http.route(['/residence/category/<int:category_id>'], type='http', auth='public', website=True, sitemap=True)
    def residence_category_detail(self, category_id, **kwargs):
        """
        Page de détail d'une catégorie
        Affiche tous les appartements disponibles dans cette catégorie
        """
        category = request.env['hotel.room.category'].sudo().browse(category_id)

        if not category.exists():
            return request.render('website.404')

        # Récupérer les appartements de cette catégorie
        rooms = category.room_ids.filtered(lambda r: r.active)

        # Récupérer les dates depuis les paramètres ou la session
        check_in = kwargs.get('check_in')
        check_out = kwargs.get('check_out')

        # Si pas de dates, essayer de récupérer depuis la commande en cours
        if not check_in or not check_out:
            sale_order = request.website.sale_get_order()
            if sale_order:
                check_in = sale_order.hotel_check_in
                check_out = sale_order.hotel_check_out

        values = {
            'category': category,
            'rooms': rooms,
            'check_in': check_in,
            'check_out': check_out,
            'page_name': 'residence_category_detail',
        }

        return request.render('hotel_room_availability.residence_category_detail_page', values)

    @http.route(['/residence/category/<int:category_id>/availability'], type='json', auth='public', website=True)
    def get_category_availability(self, category_id, **kwargs):
        """
        API JSON pour obtenir la disponibilité en temps réel d'une catégorie
        """
        category = request.env['hotel.room.category'].sudo().browse(category_id)

        if not category.exists():
            return {'error': 'Category not found'}

        return {
            'category_id': category.id,
            'category_name': category.name,
            'total_rooms': category.total_rooms,
            'available_rooms': category.available_rooms,
            'availability_display': category.get_availability_display(),
        }


class WebsiteSaleInherit(WebsiteSale):
    """
    Héritage du contrôleur WebsiteSale pour ajouter des fonctionnalités
    liées aux catégories d'appartements
    """

    @http.route()
    def shop(self, page=0, category=None, search='', min_price=0.0, max_price=0.0, ppg=False, **post):
        """
        Surcharge de la route /shop pour ajouter le filtrage par catégorie
        """
        response = super(WebsiteSaleInherit, self).shop(
            page=page,
            category=category,
            search=search,
            min_price=min_price,
            max_price=max_price,
            ppg=ppg,
            **post
        )

        # Ajouter les catégories dans les valeurs du template
        if hasattr(response, 'qcontext'):
            room_categories = request.env['hotel.room.category'].sudo().search([
                ('active', '=', True)
            ], order='sequence, name')

            response.qcontext['room_categories'] = room_categories

        return response