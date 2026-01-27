# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HotelRoomCategory(models.Model):
    """Modèle pour les catégories d'appartements de la résidence hôtelière"""

    _name = 'hotel.room.category'
    _description = 'Catégorie d\'Appartement'
    _order = 'sequence, name'

    # Informations de base
    name = fields.Char(
        string='Nom de la Catégorie',
        required=True,
        help='Ex: Appartements Meublés 2 Chambres'
    )

    active = fields.Boolean(
        string='Actif',
        default=True
    )

    sequence = fields.Integer(
        string='Séquence',
        default=10,
        help='Ordre d\'affichage des catégories'
    )

    description = fields.Text(
        string='Description',
        help='Description détaillée de la catégorie'
    )

    # Image principale (conservée pour compatibilité)
    image = fields.Binary(
        string='Image Principale',
        attachment=True,
        help='Image de couverture (sera affichée si aucune galerie n\'est définie)'
    )

    # NOUVELLE FONCTIONNALITÉ : Galerie d'images
    image_ids = fields.One2many(
        'hotel.room.category.image',
        'category_id',
        string='Galerie d\'Images',
        help='Plusieurs images pour le carousel'
    )

    image_count = fields.Integer(
        string='Nombre d\'Images',
        compute='_compute_image_count',
        store=True
    )

    # Caractéristiques
    bedroom_count = fields.Selection([
        ('2', '2 Chambres'),
        ('3', '3 Chambres'),
    ], string='Nombre de Chambres', default='2')

    is_furnished = fields.Boolean(
        string='Meublé',
        default=False,
        help='Cocher si les appartements de cette catégorie sont meublés'
    )

    # ═══════════════════════════════════════════════════════════
    # CORRECTION : Relations avec les appartements
    # ═══════════════════════════════════════════════════════════

    # Champ pour SÉLECTIONNER des appartements (Many2many)
    selected_room_ids = fields.Many2many(
        'product.product',
        'hotel_category_room_selection_rel',
        'category_id',
        'room_id',
        string='Sélectionner des Appartements',
        domain=lambda self: self._get_available_rooms_domain(),
        help='Sélectionnez les appartements à assigner à cette catégorie'
    )

    # Champ pour AFFICHER les appartements assignés (One2many)
    room_ids = fields.One2many(
        'product.product',
        'room_category_id',
        string='Appartements Assignés',
        help='Liste des appartements de cette catégorie',
        domain=[('is_room_type', '=', True)]  # ✅ CORRIGÉ : is_room_type au lieu de is_hotel_room
    )

    # Champs calculés
    total_rooms = fields.Integer(
        string='Total d\'Appartements',
        compute='_compute_room_counts',
        store=True,
        help='Nombre total d\'appartements dans cette catégorie'
    )

    available_rooms = fields.Integer(
        string='Appartements Disponibles',
        compute='_compute_room_counts',
        help='Nombre d\'appartements disponibles aujourd\'hui'
    )

    occupied_rooms = fields.Integer(
        string='Appartements Occupés',
        compute='_compute_room_counts',
        help='Nombre d\'appartements occupés'
    )

    availability_rate = fields.Float(
        string='Taux de Disponibilité (%)',
        compute='_compute_room_counts',
        help='Pourcentage d\'appartements disponibles'
    )

    # ═══════════════════════════════════════════════════════════
    # MÉTHODES
    # ═══════════════════════════════════════════════════════════

    def _get_available_rooms_domain(self):
        """
        Retourne le domain pour afficher seulement les appartements disponibles
        """
        if self.id:
            # Si la catégorie existe, afficher :
            # - Les appartements non assignés
            # - Les appartements déjà assignés à cette catégorie
            return [
                '|',
                ('room_category_id', '=', False),
                ('room_category_id', '=', self.id),
                ('is_room_type', '=', True),  # ✅ Utilise is_room_type (module parent)
            ]
        else:
            # Si nouvelle catégorie, afficher seulement les non assignés
            return [
                ('room_category_id', '=', False),
                ('is_room_type', '=', True),
            ]

    @api.onchange('selected_room_ids')
    def _onchange_selected_rooms(self):
        """
        Assigne automatiquement les appartements sélectionnés à cette catégorie
        """
        if not self.selected_room_ids:
            return

        # Assigner les nouveaux appartements
        for room in self.selected_room_ids:
            if room.room_category_id != self:
                room.room_category_id = self

    @api.depends('image_ids')
    def _compute_image_count(self):
        """Calcule le nombre d'images dans la galerie"""
        for record in self:
            record.image_count = len(record.image_ids.filtered(lambda img: img.active))

    @api.depends('room_ids', 'room_ids.active')
    def _compute_room_counts(self):
        """Calcule les statistiques de disponibilité des appartements"""
        for category in self:
            active_rooms = category.room_ids.filtered(lambda r: r.active)
            category.total_rooms = len(active_rooms)

            # Calculer les appartements disponibles
            available_count = 0
            for room in active_rooms:
                # Utilise la méthode is_available() si elle existe
                if hasattr(room, 'is_available') and callable(room.is_available):
                    if room.is_available():
                        available_count += 1
                # Sinon, utilise le champ is_available_today si disponible
                elif hasattr(room, 'is_available_today'):
                    if room.is_available_today:
                        available_count += 1
                else:
                    # Par défaut, considère disponible
                    available_count += 1

            category.available_rooms = available_count
            category.occupied_rooms = category.total_rooms - category.available_rooms

            if category.total_rooms > 0:
                category.availability_rate = (category.available_rooms / category.total_rooms) * 100
            else:
                category.availability_rate = 0.0

    def action_view_rooms(self):
        """Action pour afficher les appartements de cette catégorie"""
        self.ensure_one()
        return {
            'name': f'Appartements - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'product.product',
            'view_mode': 'kanban,tree,form',
            'domain': [('room_category_id', '=', self.id), ('is_room_type', '=', True)],
            'context': {
                'default_room_category_id': self.id,
                'default_is_room_type': True,
            }
        }

    def action_view_gallery(self):
        """Action pour afficher la galerie d'images"""
        self.ensure_one()
        return {
            'name': f'Galerie - {self.name}',
            'type': 'ir.actions.act_window',
            'res_model': 'hotel.room.category.image',
            'view_mode': 'kanban,tree,form',
            'domain': [('category_id', '=', self.id)],
            'context': {
                'default_category_id': self.id,
            }
        }

    def write(self, vals):
        """
        Surcharge pour synchroniser selected_room_ids et room_ids
        """
        res = super().write(vals)

        # Si selected_room_ids a changé, mettre à jour les assignations
        if 'selected_room_ids' in vals:
            for record in self:
                # Récupérer les appartements actuellement sélectionnés
                current_selected = record.selected_room_ids
                # Récupérer les appartements actuellement assignés
                current_assigned = record.room_ids

                # Retirer l'assignation des appartements désélectionnés
                to_unassign = current_assigned - current_selected
                if to_unassign:
                    to_unassign.write({'room_category_id': False})

                # Assigner les nouveaux appartements
                to_assign = current_selected - current_assigned
                if to_assign:
                    to_assign.write({'room_category_id': record.id})

        return res

    @api.model
    def create(self, vals):
        """
        Surcharge pour gérer selected_room_ids à la création
        """
        # Créer d'abord la catégorie
        record = super().create(vals)

        # Ensuite, assigner les appartements sélectionnés
        if record.selected_room_ids:
            record.selected_room_ids.write({'room_category_id': record.id})

        return record