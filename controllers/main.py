# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request
import random


class ResidenceCategoriesController(http.Controller):
    """Contrôleur pour afficher les catégories d'appartements sur le site web"""

    @http.route(['/residence/categories'], type='http', auth='public', website=True, sitemap=True)
    def residence_categories_list(self, **kwargs):
        """Page listant toutes les catégories d'appartements"""

        # Récupérer toutes les catégories actives
        Category = request.env['hotel.room.category']
        categories = Category.sudo().search([
            ('active', '=', True)
        ], order='sequence, name')

        values = {
            'categories': categories,
            'page_name': 'residence_categories',
        }

        return request.render('hotel_residence_category.residence_categories_page', values)

    @http.route(['/residence/category/<int:category_id>/book'], type='http', auth='public', website=True)
    def reserve_random_room(self, category_id, **kwargs):
        """
        Réserve un appartement aléatoire disponible dans la catégorie
        Redirige vers la page de réservation de l'appartement choisi
        """

        Category = request.env['hotel.room.category']
        category = Category.sudo().browse(category_id)

        # Vérifier que la catégorie existe et est active
        if not category.exists() or not category.active:
            return request.redirect('/residence/categories')

        # Récupérer les appartements disponibles de cette catégorie
        available_rooms = category.room_ids.filtered(
            lambda r: r.active and r.is_available_today
        )

        # Si aucun appartement disponible, rediriger avec message
        if not available_rooms:
            # Rediriger vers la page des catégories avec un message d'erreur
            return request.redirect('/residence/categories?error=no_availability')

        # Choisir un appartement aléatoire parmi les disponibles
        selected_room = random.choice(available_rooms)

        # Rediriger vers la page de réservation/produit de l'appartement
        # Option 1 : Vers la page produit e-commerce
        return request.redirect(f'/shop/product/{selected_room.id}')

        # Option 2 : Si vous voulez créer une réservation directement
        # return request.redirect(f'/shop/cart/update?product_id={selected_room.id}&add_qty=1')

    @http.route(['/residence/category/<int:category_id>/availability'],
                type='json', auth='public', website=True)
    def get_category_availability(self, category_id, checkin=None, checkout=None, **kwargs):
        """API JSON pour obtenir la disponibilité en temps réel d'une catégorie"""

        Category = request.env['hotel.room.category']
        category = Category.sudo().browse(category_id)

        if not category.exists():
            return {'error': 'Category not found'}

        # Calculer les appartements disponibles
        available_rooms = category.room_ids.filtered(
            lambda r: r.active and r.is_available_today
        )

        return {
            'category_id': category.id,
            'category_name': category.name,
            'total_rooms': category.total_rooms,
            'available_rooms': len(available_rooms),
            'availability_percentage': (
                        len(available_rooms) / category.total_rooms * 100) if category.total_rooms > 0 else 0,
        }