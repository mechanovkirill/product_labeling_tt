from odoo import models, fields


class PLAct(models.Model):
    _name = 'product_labeling.act'
    _description = 'Act'

    name = fields.Char()
    type = fields.Selection([('purchase', 'Purchase'), ('move', 'Move'), ('sale', 'Sale')])
    pl_product_id = fields.Many2one('product_labeling.product')
    pl_labeled_product_id = fields.Many2one('product_labeling.labeled_product')
    quantity = fields.Integer()

    state = fields.Selection(
        [('draft', 'Draft'), ('confirmed', 'Confirmed'), ('canceled', 'Canceled')], default='draft')
    current_pl_warehouse_id = fields.Many2one('product_labeling.warehouse')
    to_pl_warehouse_id = fields.Many2one('product_labeling.warehouse')
    pl_move_ids = fields.One2many('product_labeling.move', inverse_name='pl_act_id')

    def action_reset_to_draft(self):
        pass # if not sold
