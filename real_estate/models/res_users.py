from odoo import fields, models


class ResUsers(models.Model):
    _inherit = "res.users"

    # unidad 2 - punto 24
    property_ids = fields.One2many(
        "estate.property",
        "salesman_id",
        string="Propiedades",
    )