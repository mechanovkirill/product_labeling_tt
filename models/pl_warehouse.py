from odoo import models, fields


class PLWarehouse(models.Model):
    _name = 'product_labeling.warehouse'
    _description = 'Warehouse'

    name = fields.Char(required=True)
    pl_labeled_product_id = fields.One2many('product_labeling.labeled_product', 'pl_warehouse_id')
    