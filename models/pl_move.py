from odoo import models, fields


class PLMove(models.Model):
    _name = 'product_labeling.move'
    _description = 'Move'
    _inherit = 'mail.thread'

    pl_labeled_product_id = fields.Many2one('product_labeling.labeled_product')
    pl_act_id = fields.Many2one('product_labeling.act')
    pl_act_product_binder = fields.Many2one('product_labeling.act_product_binder')
    parent_act_state = fields.Selection(related='pl_act_id.state')
    date = fields.Date(related='pl_act_id.date')
    quantity = fields.Integer(string='Кол-во')

    name = fields.Char()
    debit = fields.Float(string='Прибыль')
    credit = fields.Float(string='Расход')

    def action_open_pl_move(self):
        return {
            'name': 'Move',
            'type': 'ir.actions.act_window',
            'res_model': 'product_labeling.move',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

