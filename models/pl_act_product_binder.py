from odoo import models, fields, api
from odoo.exceptions import UserError


class PLActProductBinder(models.Model):
    _name = 'product_labeling.act_product_binder'
    _description = 'act_product_binder'

    pl_act_id = fields.Many2one('product_labeling.act')
    operation_type = fields.Char(related='pl_act_id.operation_type')
    parent_act_state = fields.Selection(related='pl_act_id.state')

    pl_product_id = fields.Many2one('product_labeling.product', string="Приобретение товара")
    pl_labeled_product_id = fields.Many2one(
        'product_labeling.labeled_product', string="Товар в наличии",
        domain=[
            ('state', 'not in', ['Товар был разделен', 'Продан']),
            ('pl_warehouse_id', '=', 'pl_act_id.current_pl_warehouse_id')
        ]
    )
    quantity = fields.Integer(string="Количество")

    debit = fields.Float(string='Прибыль')
    credit = fields.Float(string='Расход')

    def name_get(self):
        res = []
        for record in self:
            name = f"{record.pl_product_id if record.pl_product_id else record.pl_labeled_product_id}"
            res.append((record.id, name))
        return res
