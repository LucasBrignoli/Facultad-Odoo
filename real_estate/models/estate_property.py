from dateutil.relativedelta import relativedelta
from odoo import api, models, fields


class EstateProperty(models.Model):
    _name = 'estate.property'
    _description = 'Propiedad'

    name = fields.Char(string="Título", required=True)
    description = fields.Text(string="Descripción")
    postcode = fields.Char(string="Código Postal")
    date_availability = fields.Date(
        string="Fecha disponibilidad",
        copy=False,
        default=lambda self: fields.Date.today() + relativedelta(months=3),
    )
    expected_price = fields.Float(string="Precio esperado")
    selling_price = fields.Float(string="Precio de venta", copy=False)
    bedrooms = fields.Integer(string="Habitaciones", default=2)
    living_area = fields.Integer(string="Superficie cubierta")
    facades = fields.Integer(string="Fachadas")
    garage = fields.Boolean(string="Garage")
    garden = fields.Boolean(string="Jardín")
    garden_orientation = fields.Selection(
        [
            ("north", "Norte"),
            ("south", "Sur"),
            ("east", "Este"),
            ("west", "Oeste"),
        ],
        default="north",
        string="Orientación del jardín",
    )
    garden_area = fields.Integer(string="Superficie jardín")
    # unidad 2 - puntos 1, 4 y 5
    total_area = fields.Integer(
        string="Superficie total",
        compute="_compute_total_area",
        store=True,
    )
    state = fields.Selection(
        [
            ("new", "Nuevo"),
            ("offer_received", "Oferta recibida"),
            ("offer_accepted", "Oferta aceptada"),
            ("sold", "Vendido"),
            ("cancelled", "Cancelado"),
        ],
        string="Estado",
        required=True,
        default="new",
        copy=False,
    )
    property_type_id = fields.Many2one(
        "estate.property.type",
        string="Tipo Propiedad",
    )
    buyer_id = fields.Many2one(
        "res.partner",
        string="Comprador",
    )
    salesman_id = fields.Many2one(
        "res.users",
        string="Vendedor",
        copy=False,
        default=lambda self: self.env.user,
    )
    tag_ids = fields.Many2many(
        "estate.property.tag",
        string="Etiquetas",
    )
    offer_ids = fields.One2many(
        comodel_name="estate.property.offer",
        inverse_name="property_id",
        string="Ofertas",
    )
    # unidad 2 - punto 7
    best_offer = fields.Float(
        string="Mejor oferta",
        compute="_compute_best_offer",
    )

    # unidad 2 - punto 5
    @api.depends("living_area", "garden_area")
    def _compute_total_area(self):
        for record in self:
            record.total_area = record.living_area + record.garden_area

    # unidad 2 - punto 7
    @api.depends("offer_ids.price")
    def _compute_best_offer(self):
        for record in self:
            record.best_offer = max(record.offer_ids.mapped("price"), default=0.0)

    # unidad 2 - punto 13
    @api.onchange("garden")
    def _onchange_garden(self):
        if self.garden:
            self.garden_area = 10
        else:
            self.garden_area = 0

    # unidad 2 - punto 14
    @api.onchange("expected_price")
    def _onchange_expected_price(self):
        # se ignora el 0 para que no salte la advertencia al abrir una propiedad nueva
        if self.expected_price and self.expected_price < 10000:
            return {
                "warning": {
                    "title": "Precio bajo",
                    "message": "El precio esperado ingresado es menor a 10.000. "
                               "Verificá que no se trate de un error de tipeo.",
                }
            }