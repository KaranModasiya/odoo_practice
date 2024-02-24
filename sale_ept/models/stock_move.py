from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.fields import Command

class StockMove(models.Model):

	_name = 'stock.move.ept'
	_description = 'Stock Move Unit'

	name = fields.Text(string="Description", help="Description of the stock move unit")
	product_id = fields.Many2one(comodel_name="product.ept", string="Product Id", help="Product Id of the stock move unit", required=True)
	uom_id = fields.Many2one(comodel_name="product.uom.ept", string="Product UoM", help="Unit of Measure of the product", required=True)
	source_location_id = fields.Many2one(comodel_name="stock.location.ept", string="Source Location", help="Stock location of the stock move unit")
	destination_location_id = fields.Many2one(comodel_name="stock.location.ept", string="Destination Location", help="Destination location of the stock move unit")
	qty_to_deliver = fields.Float(string="Demand", help="Demand of the stock move unit", readonly=True)
	qty_done = fields.Float(string="Done Quantities", help="Done quantities of the stock move unit")
	state = fields.Selection(selection=[
		('Draft', 'Draft'),
		('Done', 'Done'),
		('Cancelled', 'Cancelled'),
		], string="Status", help="Status of the stock move unit", default='Draft')
	sale_line_id = fields.Many2one(comodel_name="sale.order.line.ept", string="Sales Lines", help="Sales lines of the stock move unit")
	purchase_line_id = fields.Many2one(comodel_name="purchase.order.line.ept", string="Purchase Lines", help="Purchase lines of the stock move unit")
	stock_inventory_id = fields.Many2one(comodel_name="stock.inventory.ept", string="Stock Inventory", help="Stock inventory of the stock move unit", ondelete="cascade")
	picking_id = fields.Many2one(comodel_name="stock.picking.ept", string="Picking Id", help="Picking Id of the stock move unit", ondelete='cascade')

	@api.onchange('product_id', 'source_location_id', 'destination_location_id')
	def onchange_product_name(self):
		self.uom_id = self.product_id.uom_id.id
		self.name = f"{self.product_id.name} - {self.source_location_id.name} -> {self.destination_location_id.name}"

