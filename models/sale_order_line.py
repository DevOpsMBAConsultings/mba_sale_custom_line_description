# -*- coding: utf-8 -*-
from odoo import api, fields, models


class SaleOrderLine(models.Model):
    _inherit = 'sale.order.line'

    is_custom_name = fields.Boolean(
        string='Descripción Personalizada',
        default=False,
        copy=True,
        help='Indica si el usuario ha modificado libremente la descripción de la línea.'
    )

    @api.onchange('name')
    def _onchange_name_mark_custom(self):
        """
        Marca la línea como personalizada cuando el usuario edita la descripción directamente.
        """
        for line in self:
            if line.name and line.product_id:
                default_desc = ""
                if hasattr(line.product_id, 'get_product_multiline_description_sale'):
                    default_desc = line.product_id.get_product_multiline_description_sale()
                else:
                    default_desc = line.product_id.display_name
                
                if line.name != default_desc:
                    line.is_custom_name = True

    @api.onchange('product_id')
    def _onchange_product_id_reset_custom_name(self):
        """
        Al cambiar el producto manualmente, resetea la marca de descripción personalizada
        para permitir que el nuevo producto aplique su descripción por defecto.
        """
        for line in self:
            line.is_custom_name = False

    @api.depends('product_id', 'product_uom', 'product_uom_qty')
    def _compute_name(self):
        """
        Preserva la descripción personalizada del usuario si is_custom_name es True.
        """
        lines_to_compute = self.env['sale.order.line']
        for line in self:
            if line.is_custom_name and line.name:
                line.name = line.name
            else:
                lines_to_compute |= line
        if lines_to_compute:
            super(SaleOrderLine, lines_to_compute)._compute_name()
