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

    active = fields.Boolean(default=True)
    name = fields.Char(string="Наименование товара")
    pl_product_id = fields.Many2one('product_labeling.product', string='Наименование товара')
    description = fields.Text(related='pl_product_id.description')
    state = fields.Char(string="Текущий статус")
    quantity = fields.Integer(string="Количество")
    parent_id = fields.Many2one('product_labeling.labeled_product')
    child_ids = fields.One2many('product_labeling.labeled_product', 'parent_id')
    mark = fields.Char(size=30, string="Маркировка")
    pl_warehouse_id = fields.Many2one('product_labeling.warehouse', string="Склад")
    profit = fields.Float(string="Прибыль", compute='_compute_profit')
    pl_act_ids = fields.One2many('product_labeling.act', inverse_name='pl_labeled_product_id')
    pl_move_ids = fields.Many2many('product_labeling.move', 'pl_labeled_product_id', compute='_compute_pl_move_ids')

    def name_get(self):
        res = []
        for record in self:
            name = f"{record.pl_product_id.name} #{record.mark} {record.pl_warehouse_id}"
            res.append((record.id, name))
        return res

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            record.mark = record.pl_product_id.id
        return records

    @api.depends('pl_move_ids')
    def _compute_profit(self):
        for record in self:
            profit = 0
            moves = self.env['product_labeling.move'].search([
                ('pl_labeled_product_id', '=', record.id)
            ])
            for move in moves:
                if move.parent_act_state == 'confirmed':
                    profit += move.debit
                    profit -= move.credit
            # check if parent
            parent = record.parent_id
            if parent:
                parent_profit = (parent.profit * record.quantity) / parent.quantity
                profit += parent_profit

            record.profit = profit

    @api.depends('state', 'parent_id', 'pl_warehouse_id')
    def _compute_pl_move_ids(self):
        for record in self:
            moves = []
            if record.parent_id:
                parent_moves = record.parent_id.pl_move_ids
                for m in parent_moves:
                    moves.append(m.id)
            self_moves = self.env['product_labeling.move'].search([
                ('pl_labeled_product_id', '=', record.id)
            ])
            for move in self_moves:
                moves.append(move.id)
            if record.pl_move_ids != moves:
                record.pl_move_ids = [(6, 0, moves)]

    def action_move_labeled_product(self):
        return self._open_act_window_to_create_new(self, 'Перемещение')

    def action_sale_labeled_product(self):
        return self._open_act_window_to_create_new(self, 'Продажа')

    def _open_act_window_to_create_new(self, self_, operation: str) -> dict:
        operation_type = self.env['product_labeling.operation_type'].search([('name', '=', operation)])
        last_act_number = int(self.env['product_labeling.act'].search(
            [('pl_operation_type_id', '=', operation_type.id)],
            limit=1, order='number desc'
        ).number) + 1
        if not last_act_number:
            last_act_number = 1
        year = datetime.date.today().year
        name = f"Акт продажи #{year}/000{last_act_number}" if operation == 'Продажа' \
            else f"Акт перемещения #{year}/000{last_act_number}"

        return {
            'name': 'Sale the product',
            'type': 'ir.actions.act_window',
            'res_model': 'product_labeling.act',
            'view_mode': 'form',
            'target': 'new',
            'context': {
                'default_pl_labeled_product_id': self_.id,
                'default_pl_operation_type_id': operation_type.id,
                'default_name': name,
                'default_quantity': self_.quantity,
                'default_current_pl_warehouse_id': self_.pl_warehouse_id.id,
                'default_number': last_act_number,
            }
        }