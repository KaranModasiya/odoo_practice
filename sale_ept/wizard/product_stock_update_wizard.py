from odoo import api, models, fields
from odoo.exceptions import ValidationError
from odoo.fields import Command

class ProductStockUpdateWizard(models.TransientModel):

	_name = 'product.stock.update.ept'
	_decription = 'Product Stock Update'

	location_id = fields.Many2one(comodel_name="stock.location.ept", string="Stock Location", help="Stock location for the product stock update")
	multi_product_ids = fields.One2many(comodel_name="multi.product.stock.update.ept", inverse_name="update_stock_id", string="New One2many")
	active_product_ids = fields.Many2many(comodel_name="product.ept", string="Active Products", help="Active products to update")


	# calculating available product stock at given location
	@api.onchange('location_id')
	def onchange_location_id(self):
		if self.location_id:
			for rec in self.multi_product_ids:
				rec.available_stock = rec.product_id.with_context(location=self.location_id.id).product_stock
			# self.available_stock = self.env['product.ept'].with_context(location=self.location_id.id).browse(self._context.get('active_ids')[0]).product_stock


	# updating product stock by generating inventory adjustment if there is any difference
	def action_update_stock_button(self):
		inventory_lines = []
		for rec in self.multi_product_ids:
			if rec.difference:
				inventory_lines.append(Command.create({
					'product_id': rec.product_id.id,
					'available_qty': rec.available_stock,
					'counted_product_qty': rec.counted_qty,
					}))

		if inventory_lines:
			self.env['stock.inventory.ept'].create({
				'name': "Products - Inventory Adjustment",
				'location_id': self.location_id.id,
				'inventory_line_ids': inventory_lines,
				}).action_validate_inventory_button()


	@api.model
	def default_get(self, fields):
		product_list = []
		active_products = self.env['product.ept'].browse(self._context.get('active_ids'))
		for product in active_products:
			product_list.append(Command.create({'product_id': product.id}))
		res = super(ProductStockUpdateWizard, self).default_get(fields)
		res.update({'multi_product_ids': product_list, 'active_product_ids': active_products})
		return res
