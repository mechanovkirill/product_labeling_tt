from odoo import models, fields, api


class PLOperationType(models.Model):
    _name = 'product_labeling.operation_type'
    _description = 'operation_type'

    name = fields.Char(required=True, string='Название операции')
    product_state = fields.Char(string='Товары к которым будет применена операция будут иметь статус:', required=True)
    document_name = fields.Char(string='Паттерн имени документа')

