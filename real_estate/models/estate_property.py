import random
from dateutil.relativedelta import relativedelta
from odoo import api, Command, models, fields
from odoo.exceptions import UserError

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
    # unidad 2 - punto 19
    offer_partner_ids = fields.Many2many(
        "res.partner",
        string="Ofertantes",
        compute="_compute_offer_partner_ids",
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

    # unidad 2 - punto 19
    @api.depends("offer_ids.partner_id")
    def _compute_offer_partner_ids(self):
        for record in self:
            record.offer_partner_ids = record.offer_ids.mapped("partner_id")

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

        # unidad 2 - punto 22
    @api.ondelete(at_uninstall=False)
    def _unlink_if_new_or_cancelled(self):
        for record in self:
            if record.state not in ('new', 'cancelled'):
                raise UserError("Solo se pueden borrar propiedades nuevas o canceladas.")
    
    def action_cancel(self):
        for record in self:
            if record.state == 'sold':
                raise UserError("Una propiedad vendida no puede ser cancelada.")
            record.state = 'cancelled'
        return True

    def action_sold(self):
        for record in self:
            if record.state == 'cancelled':
                raise UserError("Una propiedad cancelada no puede ser vendida.")
            record.state = 'sold'
        return True

        # unidad 2 - punto 20
    def action_generate_offer(self):
        for record in self:
            partners = self.env['res.partner'].search([
                ('active', '=', True),
                ('id', 'not in', record.offer_partner_ids.ids),
            ])
            if not partners:
                raise UserError("No hay contactos disponibles para generar una oferta.")
            factor = random.uniform(0.7, 1.3)
            self.env['estate.property.offer'].create({
                'property_id': record.id,
                'partner_id': random.choice(partners).id,
                'price': record.expected_price * factor,
            })
        return True

        # unidad 2 - punto 21
    def action_clear_tags(self):
        for record in self:
            record.tag_ids = [Command.clear()]
        return True

    def action_load_all_tags(self):
        all_tags = self.env['estate.property.tag'].search([])
        for record in self:
            record.tag_ids = [Command.set(all_tags.ids)]
        return True

    def action_new_building_tag(self):
        tag = self.env['estate.property.tag'].search([('name', '=', 'A estrenar')], limit=1)
        if not tag:
            tag = self.env['estate.property.tag'].create({'name': 'A estrenar'})
        for record in self:
            record.tag_ids = [Command.link(tag.id)]
        return True