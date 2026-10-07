from dateutil.relativedelta import relativedelta
from odoo import api, models, fields


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Oferta sobre propiedad'

    price = fields.Float(string="Precio", required=True)
    status = fields.Selection(
        [
            ("accepted", "Aceptada"),
            ("refused", "Rechazada"),
        ],
        string="Estado",
    )
    partner_id = fields.Many2one(
        "res.partner",
        string="Ofertante",
        required=True,
    )
    property_id = fields.Many2one(
        "estate.property",
        string="Propiedad",
        required=True,
    )
    # unidad 2 - punto 9
    validity = fields.Integer(string="Validez (días)", default=7)
    # unidad 2 - puntos 9 y 10
    date_deadline = fields.Date(
        string="Fecha límite",
        compute="_compute_date_deadline",
        inverse="_inverse_date_deadline",
    )
    # unidad 2 - punto 11
    property_type_id = fields.Many2one(
        related="property_id.property_type_id",
        string="Tipo de propiedad",
        store=True,
    )

    # unidad 2 - punto 10
    @api.depends("create_date", "validity")
    def _compute_date_deadline(self):
        for record in self:
            # mientras la oferta no se guarda no tiene create_date, se usa la fecha de hoy
            start = record.create_date.date() if record.create_date else fields.Date.today()
            record.date_deadline = start + relativedelta(days=record.validity)

    def _inverse_date_deadline(self):
        for record in self:
            if not record.date_deadline:
                continue
            start = record.create_date.date() if record.create_date else fields.Date.today()
            record.validity = (record.date_deadline - start).days
