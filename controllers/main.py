# -*- coding: utf-8 -*-

from odoo import http, fields
from odoo.http import request


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

    @http.route(['/residence/category/<int:category_id>'], type='http', auth='public', website=True, sitemap=True)
    def residence_category_detail(self, category_id, **kwargs):
        """Page de détail d'une catégorie avec ses appartements"""

        Category = request.env['hotel.room.category']
        category = Category.sudo().browse(category_id)

        # Vérifier que la catégorie existe et est active
        if not category.exists() or not category.active:
            return request.redirect('/residence/categories')

        # Récupérer les appartements de cette catégorie
        rooms = category.room_ids.filtered(lambda r: r.active)

        values = {
            'category': category,
            'rooms': rooms,
            'page_name': 'residence_category_detail',
        }

        return request.render('hotel_residence_category.residence_category_detail_page', values)

    @http.route(['/residence/category/<int:category_id>/availability'],
                type='json', auth='public', website=True)
    def get_category_availability(self, category_id, checkin=None, checkout=None, **kwargs):
        """API JSON pour obtenir la disponibilité en temps réel d'une catégorie"""

        Category = request.env['hotel.room.category']
        category = Category.sudo().browse(category_id)

        if not category.exists():
            return {'error': 'Category not found'}

        # Si des dates sont fournies, on pourrait calculer la disponibilité pour ces dates
        # Pour l'instant, on retourne juste les stats actuelles

        return {
            'category_id': category.id,
            'category_name': category.name,
            'total_rooms': category.total_rooms,
            'available_rooms': category.available_rooms,
            'availability_percentage': (
                        category.available_rooms / category.total_rooms * 100) if category.total_rooms > 0 else 0,
        }