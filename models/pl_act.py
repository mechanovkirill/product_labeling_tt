import datetime
from odoo import models, fields, api
from odoo.exceptions import UserError


class PLAct(models.Model):
    _name = 'product_labeling.act'
    _description = 'Act'
    _inherit = 'mail.thread'

    name = fields.Char(string="Имя документа")
    date = fields.Date(default=datetime.date.today(), required=True, string="Дата документа")
    number = fields.Char(size=50)

    pl_operation_type_id = fields.Many2one('product_labeling.operation_type', string='Тип операции')
    operation_type = fields.Char(related='pl_operation_type_id.name')

    pl_product_id = fields.Many2one('product_labeling.product', string="Товар")
    pl_labeled_product_id = fields.Many2one('product_labeling.labeled_product', string="Товар")
    quantity = fields.Integer(string="Количество", required=True)

    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled')], default='draft')
    current_pl_warehouse_id = fields.Many2one('product_labeling.warehouse', string='Применить для товаров со склада')
    to_pl_warehouse_id = fields.Many2one('product_labeling.warehouse', string='Назначить новый склад')
    pl_move_ids = fields.One2many('product_labeling.move', inverse_name='pl_act_id')

    def action_reset_act_to_draft(self):
        pass  # if not sold

    def action_confirm_act(self):
        if not self.name:
            raise UserError('Документ должен иметь имя')
        if not self.quantity:
            raise UserError('Укажите количество единиц товара')
        if not self.to_pl_warehouse_id:
            raise UserError('Укажите склад в который перемещен товар')

        if self.pl_operation_type_id.name == 'Покупка':
            self._purchase_act_confirmation(self)
            return self.return_act_window_new(self.id)

        if not self.current_pl_warehouse_id:
            raise UserError('Укажите товар текущее местоположение товара')
        if not self.pl_labeled_product_id:
            raise UserError('Выберите товар')
        if self.quantity > self.pl_labeled_product_id.quantity:
            raise UserError('Недостаточное количество товара в наличии')
        if self.pl_labeled_product_id.state == 'Товар был разделен':
            raise UserError(
                'Данный товар был разделен на другие товары и отсутствует.'
                'Выберите другой товар.'
            )

        self._act_confirmation(self)
        return self.return_act_window_new(self.id)

    def _purchase_act_confirmation(self, act):
        if not act.pl_product_id:
            raise UserError('Выберите приобретаемый товар')

        labeled_product = self.env['product_labeling.labeled_product'].search([
            ('pl_product_id', '=', act.pl_product_id.id),
            ('pl_warehouse_id', '=', act.to_pl_warehouse_id.id),
            ('state', '=', act.pl_operation_type_id.product_state),
        ], limit=1)
        if not labeled_product:
            labeled_product = self.env['product_labeling.labeled_product'].create({
                'pl_product_id': act.pl_product_id.id,
                'mark': act.pl_product_id.id,
                'quantity': act.quantity,
                'pl_warehouse_id': act.to_pl_warehouse_id.id,
                'state': act.pl_operation_type_id.product_state,
                'name': f"{act.pl_product_id.name} #{act.pl_product_id.id} {act.to_pl_warehouse_id}"
            })
        else:
            labeled_product.quantity += act.quantity

        self.pl_labeled_product_id = labeled_product.id
        for move in act.pl_move_ids:
            move.pl_labeled_product_id = labeled_product.id

        act.state = 'confirmed'

    def _act_confirmation(self, act):
        if act.quantity == act.pl_labeled_product_id.quantity:
            act.pl_labeled_product_id.pl_warehouse_id = act.to_pl_warehouse_id
            act.pl_labeled_product_id.state = act.pl_operation_type_id.product_state
            for move in act.pl_move_ids:
                move.pl_labeled_product_id = act.pl_labeled_product_id.id
        elif act.quantity < act.pl_labeled_product_id.quantity:
            # create new product
            labeled_product_new = act.pl_labeled_product_id.copy()
            labeled_product_new.pl_move_ids = []
            labeled_product_new.quantity = act.quantity
            labeled_product_new.pl_warehouse_id = act.to_pl_warehouse_id
            labeled_product_new.state = act.pl_operation_type_id.product_state
            for move in act.pl_move_ids:
                move.pl_labeled_product_id = labeled_product_new.id

            # create remains product
            labeled_product_remain = act.pl_labeled_product_id.copy()
            labeled_product_remain.quantity -= act.quantity

            # update parent product
            act.pl_labeled_product_id.state = 'Товар был разделен'
            act.pl_labeled_product_id.pl_warehouse_id = False
            id_ = act.pl_labeled_product_id.id

            labeled_product_new.parent_id = id_
            labeled_product_remain.parent_id = id_

        act.state = 'confirmed'

    @staticmethod
    def return_act_window_new(id_):
        return {
            'name': 'Act',
            'type': 'ir.actions.act_window',
            'res_model': 'product_labeling.act',
            'view_mode': 'form',
            'res_id': id_,
            'target': 'new',
        }

    @api.onchange('pl_labeled_product_id')
    def onchange_pl_labeled_product_id(self):
        labeled_prod = self.pl_labeled_product_id
        if labeled_prod:
            self.quantity = labeled_prod.quantity
            self.current_pl_warehouse_id = labeled_prod.pl_warehouse_id
