from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.fields import Command

class PurchaseOrder(models.Model):

	_name = 'purchase.order.ept'
	_description = 'Purchase Order'

	name = fields.Char(string="Id", help="Id of the purchase order", default='New')
	warehouse_id = fields.Many2one(comodel_name="stock.warehouse.ept", string="Warehouse Name", help="Name of the warehouse")
	partner_id = fields.Many2one(comodel_name="res.partner.ept", string="Partner Name", help="Partner of the purchase order")
	order_date = fields.Date(string="Order Date", help="Date of the purchase order", default=fields.Date.today())
	state = fields.Selection(selection=[
		('Draft', 'Draft'),
		('Confirm', 'Confirm'),
		('Done', 'Done'),
		('Cancelled', 'Cancelled'),
		], string="Status", help="Status of the purchase order", default='Draft')
	purchase_order_line_ids = fields.One2many(comodel_name="purchase.order.line.ept", inverse_name="purchase_order_id", string="Partner Line", help="Purchase lines of the order")
	picking_ids = fields.One2many(comodel_name="stock.picking.ept", inverse_name="purchase_order_id", string="Stock Picking", help="Stock picking of the purchase order", readonly=True)

	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('purchase.order.ept')
		return super(PurchaseOrder, self).create(vals)


	def action_confirm_order_button(self):
		"""
		To confirm purchase order.
		Changes state of purches order record and related purchase order lines records to Confirm.
		Creates stock picking record and stock move records.
		:return: None
		"""
		if not self.purchase_order_line_ids:
			raise ValidationError('Please add some purchase lines to confirm purchase.')

		vendor = self.env['stock.location.ept'].search([('location_type', '=', 'Vendor')], limit=1)
		if not vendor:
			raise ValidationError("System couldn't find Vendor location, confirm operation cannot be completed")

		stock_moves = []
		# changing purchase lines state to confirm and creating stock moves list
		for line in self.purchase_order_line_ids:
			# creating stock move
			stock_moves.append(Command.create({
				'name': f"{line.product_id.name} - {vendor.name} -> {self.warehouse_id.stock_location_id.name}",
				'product_id': line.product_id.id,
				'uom_id': line.uom_id.id,
				'qty_to_deliver': line.quantity,
				'qty_done': 0,
				'purchase_line_id': line.id,
				'state': 'Draft',
				'source_location_id': vendor.id,
				'destination_location_id': self.warehouse_id.stock_location_id.id,
				}))
			line.state = 'Confirm'

		# generating stock picking record
		if stock_moves:
			self.env['stock.picking.ept'].create({
				'partner_id': self.partner_id.id,
				'transaction_type': 'In',
				'move_ids': stock_moves,
				'purchase_order_id': self.id,
				})

		self.state = 'Confirm'
