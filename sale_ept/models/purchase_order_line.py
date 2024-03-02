from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.fields import Command

class PurchaseOrderLine(models.Model):

	_name = 'purchase.order.line.ept'
	_description = 'Purchase Orderlines'

	purchase_order_id = fields.Many2one(comodel_name="purchase.order.ept", string="Purchase Order Id", help="Purchase order Id of the purchase order line")
	product_id = fields.Many2one(comodel_name="product.ept", string="Product Id", help="Product Id of the purchase order line")
	name = fields.Text(string="Description", help="Description of the purchase order line")
	quantity = fields.Float(string="Quantity", help="Product quantity of the purchase order line", digits=(6, 2))
	cost_price = fields.Float(string="Cost Price", help="Cost price of the product", digits=(6, 2))
	state = fields.Selection(selection=[
		('Draft', 'Draft'),
		('Confirm', 'Confirm'),
		('Done', 'Done'),
		('Cancelled', 'Cancelled'),
		], string="Status", help="Status of the purchase order line", default='Draft')
	uom_id = fields.Many2one(comodel_name="product.uom.ept", string="Product UoM", help="Unit of Measure of the Product")
	purchase_stock_move_ids = fields.One2many(comodel_name="stock.move.ept", inverse_name="purchase_line_id", string="Stock Moves", help="Stock moves of the purchase order line")
	received_qty = fields.Float(compute="_compute_qty", string="Received Quantity", help="Received quantity of the product", digits=(6, 2))
	cancelled_qty = fields.Float(compute="_compute_qty", string="cancelled Quantity", help="Cancelled quantity of the product", digits=(6, 2))
	pending_qty = fields.Float(compute="_compute_qty", string="Pending Quantity", help="Pending quantity of the product", digits=(6, 2))


	@api.onchange('product_id')
	def onchange_product(self):
		if self.product_id:
			self.uom_id = self.product_id.uom_id.id
			self.name = f"{self.product_id.name}"
			self.quantity = 1
			self.cost_price = self.product_id.cost_price
		else:
			self.quantity = 0


	@api.depends('purchase_stock_move_ids')
	def _compute_qty(self):
		for purchase_line in self:
			received = sum(purchase_line.purchase_stock_move_ids.filtered_domain([('state', '=', 'Done')]).mapped('qty_done'))
			cancelled = sum(purchase_line.purchase_stock_move_ids.filtered_domain([('state', '=', 'Cancelled')]).mapped('qty_done'))

			purchase_line.received_qty = received
			purchase_line.cancelled_qty = cancelled
			purchase_line.pending_qty = purchase_line.quantity - (received - cancelled)
