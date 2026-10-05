from odoo import models, fields


class EstatePropertyType(models.Model):
    _name = 'estate.property.type'

    name = fields.Char(string="Nombre", required=True)
