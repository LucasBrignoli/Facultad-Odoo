from odoo import models, fields


class EstatePropertyTag(models.Model):
    _name = 'estate.property.tag'
    _description = 'Etiqueta de propiedad'

    _unique_tag_name = models.Constraint(
    'UNIQUE(name)', 'El nombre de la etiqueta debe ser único',
    )

    name = fields.Char(string="Nombre", required=True)
