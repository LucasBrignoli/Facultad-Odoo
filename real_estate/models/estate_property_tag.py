from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Etiqueta de propiedad'

    name = fields.Char(string="Nombre", required=True)
