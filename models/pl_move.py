from odoo import models, fields


class PLMove(models.Model):
    _name = 'product_labeling.move'
    _description = 'Move'
    _inherit = 'mail.thread'

    pl_labeled_product_id = fields.Many2one('product_labeling.labeled_product')
    pl_act_id = fields.Many2one('product_labeling.act')
    parent_act_state = fields.Selection(related='pl_act_id.state')
    date = fields.Date(related='pl_act_id.date')

    name = fields.Char()
    debit = fields.Float()
    credit = fields.Float()

    def action_open_pl_move(self):
        return {
            'name': 'Move',
            'type': 'ir.actions.act_window',
            'res_model': 'product_labeling.move',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

