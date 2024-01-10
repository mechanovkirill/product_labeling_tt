import datetime
from odoo import models, fields, api


class LabelingProduct(models.Model):
    _name = 'product_labeling.product'
    _description = 'Product'
    _inherit = 'mail.thread'

    name = fields.Char()
    description = fields.Text()

    def action_pl_buy(self):
        operation_type = self.env['product_labeling.operation_type'].search([('name', '=', 'Покупка')])
        last_purchase_act_number = int(self.env['product_labeling.act'].search(
            [('pl_operation_type_id', '=', operation_type.id)],
            limit=1, order='number desc'
        ).number) + 1
        if not last_purchase_act_number:
            last_purchase_act_number = 1
        year = datetime.date.today().year
        name = f"Акт приобретения товара #{year}/000{last_purchase_act_number}"

        return {
            'name': 'Purchase of product',
            'type': 'ir.actions.act_window',
            'res_model': 'product_labeling.act',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_pl_product_id': self.id,
                'default_pl_operation_type_id': operation_type.id,
                'default_name': name,
                'default_number': last_purchase_act_number,
            }
        }



class LabeledProduct(models.Model):
    _name = 'product_labeling.labeled_product'
    _description = 'Labeled product'
    _inherit = 'mail.thread'

    pl_product_id = fields.Many2one('product_labeling.product', string='Product')
    description = fields.Text(related='pl_product_id.description')
    state = fields.Char()
    quantity = fields.Integer()
    # parent_id = fields.Many2one('product_labeling.labeled_product')
    mark = fields.Char(size=30, default='id')
    pl_warehouse_id = fields.Many2one('product_labeling.warehouse')
    profit = fields.Float()
    pl_act_ids = fields.One2many('product_labeling.act', inverse_name='pl_labeled_product_id')

    def name_get(self):
        res = []
        for record in self:
            name = f"{record.product.name} # {record.mark}"
            res.append((record.id, name))
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record.mark = record.id
        return records

