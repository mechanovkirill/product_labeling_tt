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

    pl_act_product_binder_ids = fields.One2many('product_labeling.act_product_binder', 'pl_act_id')
    pl_labeled_product_ids = fields.Many2many('product_labeling.labeled_product', string="Товар")

    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled')], default='draft')

    current_pl_warehouse_id = fields.Many2one('product_labeling.warehouse', string='Применить для товаров со склада')
    to_pl_warehouse_id = fields.Many2one('product_labeling.warehouse', string='Назначить новый склад')

    common_expenses_move_ids = fields.Many2many(
        'product_labeling.move', string='Общие расходы',
        relation='act_id_common_expen_move_id', column1='act_id', column2='common_expen_move_id'
    )

    pl_move_ids = fields.One2many('product_labeling.move', inverse_name='pl_act_id')

    def action_reset_act_to_draft(self):
        pass  # if not sold

    def action_confirm_act(self):
        if not self.name:
            raise UserError('Документ должен иметь имя')
        if not self.to_pl_warehouse_id:
            raise UserError('Укажите склад в который перемещен товар')
        if not self.pl_act_product_binder_ids:
            raise UserError('Добавьте товары')

        if self.pl_operation_type_id.name == 'Покупка':
            self._purchase_act_confirmation(self)
            return True

        if not self.current_pl_warehouse_id:
            raise UserError('Укажите товар текущее местоположение товара')

        self._act_confirmation(self)
        return True

    def _purchase_act_confirmation(self, act):
        move_qty = 0
        for binder in act.pl_act_product_binder_ids:
            if not binder.pl_product_id:
                raise UserError('Выберите приобретаемый товар')
            if not binder.quantity:
                raise UserError('Не указано количество товара')
            if not binder.pl_move_ids:
                raise UserError('Не добавлены значения приходов/расходов для товара')
            move_qty += 1
        if act.common_expenses_move_ids:
            self._create_moves_from_common_expenses(act, move_qty)

        for binder in act.pl_act_product_binder_ids:
            labeled_product = self.env['product_labeling.labeled_product'].create({
                'pl_product_id': binder.pl_product_id.id,
                'mark': binder.pl_product_id.id,
                'quantity': binder.quantity,
                'pl_warehouse_id': act.to_pl_warehouse_id.id,
                'state': act.pl_operation_type_id.product_state,
                'name': f"{binder.pl_product_id.name} #{binder.pl_product_id.id} {act.to_pl_warehouse_id.name}",
                'pl_act_ids': [(4, act.id, 0)]
            })
            binder.pl_labeled_product_id = labeled_product.id
            binder.name = f"{binder.pl_labeled_product_id.name}"
            for move in binder.pl_move_ids:
                move.pl_labeled_product_id = labeled_product.id
                move.quantity = binder.quantity

        act.state = 'confirmed'

    def _act_confirmation(self, act):
        move_qty = 0
        for binder in act.pl_act_product_binder_ids:
            if not binder.pl_labeled_product_id:
                raise UserError('Выберите товар')
            if binder.quantity > binder.pl_labeled_product_id.quantity:
                raise UserError('Недостаточное количество товара в наличии')
            if binder.pl_labeled_product_id.state == 'Товар был разделен':
                raise UserError(
                    'Данный товар был разделен на другие товары и отсутствует.'
                    'Выберите другой товар.'
                )
            move_qty += 1
        if act.common_expenses_move_ids:
            self._create_moves_from_common_expenses(act, move_qty)

        for binder in act.pl_act_product_binder_ids:
            binder.name = f"{binder.pl_labeled_product_id.name}"
            if binder.quantity == binder.pl_labeled_product_id.quantity:
                binder.pl_labeled_product_id.pl_warehouse_id = act.to_pl_warehouse_id
                binder.pl_labeled_product_id.state = act.pl_operation_type_id.product_state
                for move in binder.pl_move_ids:
                    move.pl_labeled_product_id = binder.pl_labeled_product_id.id
                    move.quantity = binder.quantity
            elif binder.quantity < binder.pl_labeled_product_id.quantity:
                # create new product
                labeled_product_new = binder.pl_labeled_product_id.copy()
                labeled_product_new.pl_move_ids = []
                labeled_product_new.quantity = binder.quantity
                labeled_product_new.pl_warehouse_id = act.to_pl_warehouse_id
                labeled_product_new.state = act.pl_operation_type_id.product_state
                for move in binder.pl_move_ids:
                    move.pl_labeled_product_id = labeled_product_new.id
                    move.quantity = binder.quantity

                # create remains product
                labeled_product_remain = binder.pl_labeled_product_id.copy()
                labeled_product_remain.quantity -= binder.quantity

                # update parent product
                binder.pl_labeled_product_id.state = 'Товар был разделен'
                id_ = binder.pl_labeled_product_id.id

                labeled_product_new.parent_id = id_
                labeled_product_remain.parent_id = id_

        act.state = 'confirmed'

    @staticmethod
    def _create_moves_from_common_expenses(act, move_qty):
        for binder in act.pl_act_product_binder_ids:
            for expense in act.common_expenses_move_ids:
                if not expense.name:
                    raise UserError('Укажите цель оплаты для Общие Прибыли/Расходы')
                if not expense.debit and not expense.credit:
                    raise UserError('Не установлена ни одна сумма для строки Общие Прибыли/Расходы')
                move = act.env['product_labeling.move'].create({
                    'pl_act_id': act.id,
                    'pl_act_product_binder_id': binder.id,
                    'name': expense.name,
                    'debit': expense.debit / move_qty,
                    'credit': expense.credit / move_qty
                })

    @api.onchange('pl_operation_type_id')
    def onchange_pl_operation_type_id(self):
        operation_type = self.pl_operation_type_id
        if operation_type:
            last_act_number = int(self.env['product_labeling.act'].search(
                [
                    ('pl_operation_type_id', '=', operation_type.id),
                    ('state', '=', 'confirmed')
                ],
                limit=1, order='number'
            ).number)
            last_act_number += 1
            year = datetime.date.today().year

            name = f"{operation_type.document_name} #{year}/000{last_act_number}"
            self.name = name
            self.number = last_act_number

