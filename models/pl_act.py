import datetime
from odoo import models, fields


class PLAct(models.Model):
    _name = 'product_labeling.act'
    _description = 'Act'
    _inherit = 'mail.thread'

    name = fields.Char(string="Имя документа")
    date = fields.Date(default=datetime.date.today(), required=True, string="Дата документа")
    number = fields.Char(size=50)

    type = fields.Selection([('purchase', 'Purchase'), ('move', 'Move'), ('sale', 'Sale')], string="Тип операции")
    pl_product_id = fields.Many2one('product_labeling.product', string="Товар")
    pl_labeled_product_id = fields.Many2one('product_labeling.labeled_product', string="Товар")
    quantity = fields.Integer(string="Количество")

    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled')], default='draft')
    current_pl_warehouse_id = fields.Many2one('product_labeling.warehouse', string='Применить для товаров со склада')
    to_pl_warehouse_id = fields.Many2one('product_labeling.warehouse', string='Назначить новый склад')
    pl_move_ids = fields.One2many('product_labeling.move', inverse_name='pl_act_id')

    def action_reset_to_draft(self):
        pass # if not sold
