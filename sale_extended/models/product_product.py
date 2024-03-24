from odoo import api, models, fields
from odoo.fields import Command

class ProductProduct(models.Model):
	_inherit = 'product.product'

	deposit_product_id = fields.Many2one("product.product", string="Deposit Product")
	deposit_product_qty = fields.Integer(string="Product Quantity")
	deposit_product_id2 = fields.Many2one("product.product", string="Deposit Product 2")
	deposit_product_qty2 = fields.Integer(string="Product Quantity 2")
