from odoo import models, fields, api


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

    @api.model_create_multi
    def create(self, vals_list):
        records = super().create(vals_list)
        for record in records:
            if record.pl_act_product_binder:
                record.pl_act_id = record.pl_act_product_binder.pl_act_id
        return records

    def action_open_pl_move(self):
        return {
            'name': 'Move',
            'type': 'ir.actions.act_window',
            'res_model': 'product_labeling.move',
            'view_mode': 'form',
            'res_id': self.id,
            'target': 'new',
        }

