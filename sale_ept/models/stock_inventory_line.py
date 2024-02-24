from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.fields import Command

class StockInventoryLine(models.Model):

	_name = 'stock.inventory.line.ept'
	_description = 'Stock Inventory Line'

	product_id = fields.Many2one(comodel_name="product.ept", string="Product Id", help="Product Id of the stock inventory line")
	available_qty = fields.Float(string="System Quantity", help="System quantity of the stock inventory line")
	counted_product_qty = fields.Float(string="Counted Quantity", help="Counted product quantity of the stock inventory line")
	difference = fields.Float(compute="_compute_diff", string="Difference in Quantity", help="Difference in quantity of the stock inventory line", store=False, default=0)
	inventory_id = fields.Many2one(comodel_name="stock.inventory.ept", string="Inventory Id", help="Inventory Id of the stock inventory line")


	@api.depends('available_qty', 'counted_product_qty')
	def _compute_diff(self):
		for product in self:
			product.difference = product.counted_product_qty - product.available_qty
