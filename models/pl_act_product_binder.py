from odoo import models, fields, api
from odoo.exceptions import UserError


class PLActProductBinder(models.Model):
    _name = 'product_labeling.act_product_binder'
    _description = 'act_product_binder'

    name = fields.Char(size=50)
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

    debit = fields.Float(string='Прибыль', compute='_compute_binder_debit_credit')
    credit = fields.Float(string='Расход')
    pl_move_ids = fields.One2many('product_labeling.move', inverse_name='pl_act_product_binder_ids')

    def name_get(self):
        res = []
        for record in self:
            name = f"{record.pl_product_id.name if record.pl_product_id else record.pl_labeled_product_id.name}"
            res.append((record.id, name))
        return res

    def action_add_profit_expense(self):
        return {
            'name': 'Move',
            'type': 'ir.actions.act_window',
            'res_model': 'product_labeling.act_product_binder',
            'res_id': self.id,
            'view_mode': 'form',
            'target': 'new',
        }

    @api.depends('pl_move_ids')
    def _compute_binder_debit_credit(self):
        for record in self:
            debit = 0
            credit = 0
            moves = record.pl_move_ids
            if moves:
                for move in moves:
                    debit += move.debit
                    credit += move.credit

            record.debit = debit
            record.credit = credit
