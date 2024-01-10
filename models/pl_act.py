import datetime
from odoo import models, fields
from odoo.exceptions import UserError


class PLAct(models.Model):
    _name = 'product_labeling.act'
    _description = 'Act'
    _inherit = 'mail.thread'

    name = fields.Char(string="Имя документа")
    date = fields.Date(default=datetime.date.today(), required=True, string="Дата документа")
    number = fields.Char(size=50)

    pl_operation_type_id = fields.Many2one('product_labeling.operation_type')
    pl_product_id = fields.Many2one('product_labeling.product', string="Товар")
    pl_labeled_product_id = fields.Many2one('product_labeling.labeled_product', string="Товар")
    quantity = fields.Integer(string="Количество", required=True)

    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled')], default='draft')
    current_pl_warehouse_id = fields.Many2one('product_labeling.warehouse', string='Применить для товаров со склада')
    to_pl_warehouse_id = fields.Many2one('product_labeling.warehouse', string='Назначить новый склад')
    pl_move_ids = fields.One2many('product_labeling.move', inverse_name='pl_act_id')

    def action_reset_to_draft(self):
        pass # if not sold

    def action_confirm_act(self):
        if not self.name:
            raise UserError('Документ должен иметь имя')
        if not self.quantity:
            raise UserError('Укажите количество единиц товара')

        if self.type == 'purchase':
            self._purchase_act_confirmation(self)

    def _purchase_act_confirmation(self, act):
        if not act.pl_product_id:
            raise UserError('Выберите приобретаемый товар')
        if not act.to_pl_warehouse_id:
            raise UserError('Укажите склад в который перемещен товар')

        # act.state = 'confirmed'