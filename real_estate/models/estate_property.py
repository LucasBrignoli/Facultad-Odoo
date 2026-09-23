from odoo import models, fields


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Propiedad'

    name = fields.Char(string='Nombre Propiedad', required=True)
    expected_price = fields.Float(string='Precio Esperado')
