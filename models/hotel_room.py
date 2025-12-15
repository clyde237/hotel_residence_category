# -*- coding: utf-8 -*-

from odoo import models, fields, api


class ProductProduct(models.Model):
    _inherit = 'product.product'

    category_id = fields.Many2one(
        'hotel.room.category',
        string='Catégorie',
        ondelete='restrict',
        help="Catégorie de l'appartement (meublé/non-meublé, 2/3 chambres)"
    )

    bedroom_count = fields.Selection([
        ('2', '2 Chambres'),
        ('3', '3 Chambres'),
    ], string='Nombre de chambres')

    is_furnished = fields.Boolean(
        string='Meublé',
        default=False
    )

    @api.onchange('bedroom_count', 'is_furnished')
    def _onchange_auto_assign_category(self):
        """Assigne automatiquement la catégorie selon le nombre de chambres et meublé/non-meublé"""
        if self.bedroom_count and self.is_furnished is not False:
            category = self.env['hotel.room.category'].search([
                ('bedroom_count', '=', self.bedroom_count),
                ('is_furnished', '=', self.is_furnished),
            ], limit=1)

            if category:
                self.category_id = category.id

    def is_available(self, checkin_date=None, checkout_date=None):
        """
        Vérifie si la chambre est disponible pour une période donnée
        Si aucune date n'est fournie, vérifie la disponibilité actuelle
        """
        self.ensure_one()

        if not checkin_date:
            checkin_date = fields.Date.today()
        if not checkout_date:
            checkout_date = fields.Date.today()

        # Chercher les réservations qui se chevauchent
        BookingLine = self.env['hotel.booking.line']

        overlapping_bookings = BookingLine.search([
            ('product_id', '=', self.id),
            ('status_bar', 'in', ['confirm', 'allot']),
            '|',
            '&',
            ('check_in', '<=', checkin_date),
            ('check_out', '>=', checkin_date),
            '&',
            ('check_in', '<=', checkout_date),
            ('check_out', '>=', checkout_date),
        ], limit=1)

        return not overlapping_bookings


class ProductTemplate(models.Model):
    _inherit = 'product.template'

    # Ajout des champs sur le template pour faciliter la configuration
    bedroom_count_template = fields.Selection([
        ('2', '2 Chambres'),
        ('3', '3 Chambres'),
    ], string='Nombre de chambres')

    is_furnished_template = fields.Boolean(
        string='Meublé',
        default=False
    )