from dateutil.relativedelta import relativedelta
from odoo import api, models, fields
from odoo.exceptions import UserError


class EstatePropertyOffer(models.Model):
    _name = 'estate.property.offer'
    _description = 'Oferta sobre propiedad'

    _unique_partner_property = models.Constraint(
    'UNIQUE(partner_id, property_id)',
    'Una misma persona no puede hacer más de una oferta sobre la misma propiedad',
    )

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
        ondelete="cascade",
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

    # unidad 2 - punto 16
    def action_accept(self):
        for offer in self:
            offer.status = 'accepted'
            offer.property_id.buyer_id = offer.partner_id
            offer.property_id.selling_price = offer.price
            offer.property_id.state = 'offer_accepted'
            (offer.property_id.offer_ids - offer).write({'status': 'refused'})
        return True

    # unidad 2 - punto 23
    @api.model_create_multi
    def create(self, vals_list):
        for vals in vals_list:
            prop = self.env['estate.property'].browse(vals['property_id'])
            if prop.state not in ('new', 'offer_received'):
                raise UserError(
                    "Solo se pueden crear ofertas sobre propiedades nuevas o con oferta recibida."
                )
            if vals['price'] <= prop.best_offer:
                raise UserError(
                    "La oferta debe ser mayor a la mejor oferta actual (%s)." % prop.best_offer
                )
        offers = super().create(vals_list)
        for offer in offers:
            offer.property_id.state = 'offer_received'
        return offers