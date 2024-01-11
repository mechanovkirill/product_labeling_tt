from odoo import models, fields, api
from odoo.exceptions import UserError


class PLActProductBinder(models.Model):
    _name = 'product_labeling.act_product_binder'
    _description = 'act_product_binder'

    pl_act_id = fields.Many2one('product_labeling.act')
    operation_type = fields.Char(related='pl_act_id.operation_type')
    parent_act_state = fields.Selection(related='pl_act_id.state')

    pl_product_id = fields.Many2one('product_labeling.product', string="Товар")
    pl_labeled_product_id = fields.Many2one('product_labeling.labeled_product', string="Товар")
    quantity = fields.Integer(string="Количество")

    debit = fields.Float(string='Прибыль')
    credit = fields.Float(string='Расход')
