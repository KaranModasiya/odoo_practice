from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.fields import Command


class StockInventory(models.Model):

	_name = 'stock.inventory.ept'
	_description = 'Stock Inventory'

	name = fields.Char(string="Inventory Name", help="Name of the stock inventory", required=True)
	state = fields.Selection(selection=[
		('Draft', 'Draft'),
		('In-Progress', 'In-Progress'),
		('Done', 'Done'),
		('Cancelled', 'Cancelled'),
		], string="Status", help="Status of the stock inventory", default='Draft')
	location_id = fields.Many2one(comodel_name="stock.location.ept", string="Location", help="Location of the stock inventory", required=True)
	inventory_date = fields.Date(string="Inventory Date", help="Date of the stock inventory", default=fields.Date.today())
	inventory_line_ids = fields.One2many(comodel_name="stock.inventory.line.ept", inverse_name="inventory_id", string="Inventory Lines", help="Inventory lines of the stock inventory", required=True)
	stock_move_ids = fields.One2many(comodel_name="stock.move.ept", inverse_name="stock_inventory_id", string="Stock Moves", help="Stock moves of the stock inventory", required=True)


	def action_start_inventory_button(self):
		"""
		To change state in-progress.
		:return: None
		"""
		self = self.with_context(location=self.location_id.id)

		for product in self.inventory_line_ids:
			# product.available_qty = product.product_id.with_context(location=self.location_id.id).product_stock
			product.available_qty = product.product_id.product_stock

		self.state = 'In-Progress'


	def action_validate_inventory_button(self):
		"""
		To validate the inventory and generate stock moves.
		:return: None
		"""

		inventory_loss_location = self.env['stock.location.ept'].search([('location_type', '=', 'Inventory Loss')], limit=1)
		if not inventory_loss_location:
			raise ValidationError("System couldn't find Inventory loss location, validation operation cannot be completed")

		for product in self.inventory_line_ids:
			# if difference is not 0 then create a stock move with basic product details
			if product.difference != 0:
				source = inventory_loss_location if product.difference > 0 else self.location_id
				destination = self.location_id if product.difference > 0 else inventory_loss_location
				self.env['stock.move.ept'].create({
					'name': f"{product.product_id.name} - {source.name} -> {destination.name}",
					'product_id': product.product_id.id,
					'uom_id': product.product_id.uom_id.id,
					'qty_to_deliver': abs(product.difference),
					'qty_done': abs(product.difference),
					'state': 'Done',
					'stock_inventory_id': self.id,
					'source_location_id': source.id,
					'destination_location_id': destination.id,
					})
		self.state = 'Done'


	def action_cancel_inventory_button(self):
		"""
		To cancel the inventory
		:return: None
		"""
		self.state = 'Cancelled'

