from odoo import models, fields


class PLMove(models.Model):
    _name = 'product_labeling.move'
    _description = 'Move'
    _inherit = 'mail.thread'

    pl_labeled_product_id = fields.Many2one('product_labeling.labeled_product')
    pl_act_id = fields.Many2one('product_labeling.act')
    parent_act_state = fields.Selection(related='pl_act_id.state')

    name = fields.Char()
    debit = fields.Float()
    credit = fields.Float()

