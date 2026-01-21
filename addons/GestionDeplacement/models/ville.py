from odoo import models, fields, api

class Ville(models.Model):
    _name = 'gestion.ville'
    _description = 'Ville'
    _order = 'name'

    name = fields.Char(string='Nom de la ville', required=True)
    country_id = fields.Many2one('res.country', string='Pays', required=True)

    _sql_constraints = [
        ('name_country_unique', 'unique(name, country_id)', 'Une ville avec ce nom existe déjà pour ce pays.')
    ]

