from odoo import Command, models
from odoo.exceptions import UserError


class EstateProperty(models.Model):
    _inherit = "estate.property"

    # unidad 2 - punto 27
    def action_sold(self):
        res = super().action_sold()
        for record in self:
            if not record.buyer_id:
                raise UserError("La propiedad necesita un comprador para generar la factura.")
            self.env['account.move'].create({
                'partner_id': record.buyer_id.id,
                'move_type': 'out_invoice',
                'invoice_line_ids': [
                    Command.create({
                        'name': record.name,
                        'quantity': 1,
                        'price_unit': record.selling_price,
                    }),
                    Command.create({
                        'name': 'Gastos administrativos',
                        'quantity': 1,
                        'price_unit': 100,
                    }),
                ],
            })
        return res