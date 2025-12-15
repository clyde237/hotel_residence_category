# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HotelRoomCategory(models.Model):
    _name = 'hotel.room.category'
    _description = 'Catégorie de chambre/appartement'
    _order = 'sequence, name'

    name = fields.Char(
        string='Nom de la catégorie',
        required=True,
        help="Ex: Appartement meublé 3 chambres"
    )

    code = fields.Char(
        string='Code',
        required=True,
        help="Code unique pour identifier la catégorie"
    )

    sequence = fields.Integer(
        string='Séquence',
        default=10,
        help="Ordre d'affichage sur le site"
    )

    bedroom_count = fields.Selection([
        ('2', '2 Chambres'),
        ('3', '3 Chambres'),
    ], string='Nombre de chambres', required=True)

    is_furnished = fields.Boolean(
        string='Meublé',
        default=False,
        help="Cochez si l'appartement est meublé"
    )

    room_ids = fields.One2many(
        'product.product',
        'category_id',
        string='Appartements',
        domain=[('is_room_type', '=', True)],
        help="Liste des appartements dans cette catégorie"
    )

    total_rooms = fields.Integer(
        string='Total appartements',
        compute='_compute_room_stats',
        store=False,
        help="Nombre total d'appartements dans cette catégorie"
    )

    available_rooms = fields.Integer(
        string='Appartements disponibles',
        compute='_compute_room_stats',
        store=False,
        help="Nombre d'appartements disponibles actuellement"
    )

    description = fields.Text(
        string='Description',
        help="Description de la catégorie pour le site web"
    )

    image = fields.Binary(
        string='Image',
        help="Image représentative de la catégorie"
    )

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    @api.depends('room_ids', 'room_ids.is_room_type')
    def _compute_room_stats(self):
        """Calcule le nombre total et disponible d'appartements par catégorie"""
        for category in self:
            # Nombre total d'appartements dans cette catégorie
            category.total_rooms = len(category.room_ids)

            # Nombre d'appartements disponibles
            available_count = 0

            for room in category.room_ids:
                if self._check_room_availability(room):
                    available_count += 1

            category.available_rooms = available_count

    def _check_room_availability(self, room):
        """
        Vérifie si une chambre est disponible en vérifiant les réservations actives
        """
        # Récupérer la date du jour
        today = fields.Date.today()

        # Chercher les réservations actives pour cette chambre
        BookingLine = self.env['hotel.booking.line']

        active_bookings = BookingLine.search([
            ('product_id', '=', room.id),
            ('status_bar', 'in', ['confirm', 'allot']),  # États actifs
            ('check_in', '<=', today),
            ('check_out', '>=', today),
        ], limit=1)

        # Si aucune réservation active, la chambre est disponible
        return not active_bookings

    def get_availability_display(self):
        """Retourne le texte de disponibilité formaté (ex: '10/20')"""
        self.ensure_one()
        return f"{self.available_rooms}/{self.total_rooms}"

    def get_website_url(self):
        """Retourne l'URL de la page de catégorie sur le site"""
        self.ensure_one()
        return f"/residence/category/{self.id}"

    def action_view_rooms(self):
        """Ouvre la liste des appartements de cette catégorie"""
        self.ensure_one()
        return {
            'name': f'Appartements - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_mode': 'kanban,tree,form',
            'domain': [('id', 'in', self.room_ids.ids)],
            'context': {
                'default_category_id': self.id,
                'default_is_room_type': True,
                'default_bedroom_count': self.bedroom_count,
                'default_is_furnished': self.is_furnished,
            },
        }