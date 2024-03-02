from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.fields import Command

class MultiProductStockUpdateWizard(models.TransientModel):

	_name = 'multi.product.stock.update.ept'
	_decription = 'Product Stock Update'

	product_id = fields.Many2one(comodel_name="product.ept", string="Product", help="Product for stock adjustment")
	update_stock_id = fields.Many2one(comodel_name="product.stock.update.ept", string="Wizard id", help="Transient model id")
	available_stock = fields.Float(string="System Quantity", help="Available system quantity of the product")
	counted_qty = fields.Float(string="Counted Quantity", help="Counted quantity of the product")
	difference = fields.Float(compute="_compute_difference", string="Difference", help="Difference of counted quantity and system quantity of the product")



	# computing difference of available stock and counted stock
	@api.depends('counted_qty', 'available_stock')
	def _compute_difference(self):
		for product in self:
			product.difference = product.counted_qty - product.available_stock


