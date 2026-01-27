# -*- coding: utf-8 -*-

from odoo import models, fields, api


class HotelRoomCategoryImage(models.Model):
    """Modèle pour stocker plusieurs images par catégorie d'appartement"""

    _name = 'hotel.room.category.image'
    _description = 'Images de Catégorie d\'Appartement'
    _order = 'sequence, id'

    name = fields.Char(
        string='Nom',
        help='Nom descriptif de l\'image (optionnel)'
    )

    sequence = fields.Integer(
        string='Séquence',
        default=10,
        help='Ordre d\'affichage des images dans le carousel'
    )

    image = fields.Binary(
        string='Image',
        required=True,
        attachment=True,
        help='Image à afficher dans la galerie'
    )

    category_id = fields.Many2one(
        'hotel.room.category',
        string='Catégorie',
        required=True,
        ondelete='cascade',
        help='Catégorie d\'appartement associée'
    )

    active = fields.Boolean(
        string='Actif',
        default=True,
        help='Décocher pour masquer l\'image sans la supprimer'
    )

    # Champs calculés pour faciliter l'affichage
    image_medium = fields.Binary(
        string='Image Moyenne',
        compute='_compute_image_medium',
        store=True
    )

    @api.depends('image')
    def _compute_image_medium(self):
        """Crée une version moyenne de l'image pour optimiser l'affichage"""
        for record in self:
            record.image_medium = record.image