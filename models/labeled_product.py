from odoo import models, fields, api


class LabelingProduct(models.Model):
    _name = 'product_labeling.product'
    _description = 'Product'
    _inherit = 'mail.thread'

    name = fields.Char(required=True)
    description = fields.Text()



class LabeledProduct(models.Model):
    _name = 'product_labeling.labeled_product'
    _description = 'Labeled product'
    _inherit = 'mail.thread'

    pl_product_id = fields.Many2one('product_labeling.product', string='Product')
    description = fields.Text(related='pl_product_id.description')
    state = fields.Selection([('storage', 'Storage'), ('sold', 'Sold')], default='storage')
    quantity = fields.Integer()
    # parent_id = fields.Many2one('product_labeling.labeled_product')
    mark = fields.Char(size=30)
    pl_warehouse_id = fields.Many2one('product_labeling.warehouse')
    expenses = fields.Float(digits=2)
    profit = fields.Float(digits=2)
    pl_act_ids = fields.One2many('product_labeling.act', inverse_name='pl_labeled_product_id')

    def name_get(self):
        res = []
        for record in self:
            name = f"{record.product.name} # {record.mark}"
            res.append((record.id, name))
        return res

