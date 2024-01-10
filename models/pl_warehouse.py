from odoo import models, fields


class PLWarehouse(models.Model):
    _name = 'product_labeling.warehouse'
    _description = 'Warehouse'

    name = fields.Char(required=True)
    