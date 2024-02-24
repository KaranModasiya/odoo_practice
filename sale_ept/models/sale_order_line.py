from odoo import fields, models, api


class SaleOrderLine(models.Model):
	_name = 'sale.order.line.ept'
	_description = 'Sale Order Lines'

	order_id = fields.Many2one(comodel_name="sale.order.ept", string="Order ID", help="Order Id of the orderline")
	product_id = fields.Many2one(comodel_name="product.ept", string="Product ID", help="Product Id of the orderline")
	name = fields.Text(string="Description", help="Description of the orderline")
	quantity = fields.Float(string="Quantity", help="Quantity of the product", digits=(6, 2))
	unit_price = fields.Float(string="Unit Price", help="Unit price of the product", digits=(6, 2))
	uom_id = fields.Many2one(comodel_name="product.uom.ept", string="Product UOM", help="UOM of the product")
	state = fields.Selection(selection=[
		('Draft', 'Draft'),
		('Confirmed', 'Confirmed'),
		('Cancelled', 'Cancelled')
		], string="Status", help="Status of the orderline", default="Draft")
	subtotal_without_tax = fields.Float(compute="_compute_subtotal", string="Subtotal", help="Subtotal without tax of the product", digits=(6, 2), store=True)
	stock_move_ids = fields.One2many(comodel_name="stock.move.ept", inverse_name="sale_line_id", string="Stock Moves", help="Stock moves of the orderline", readonly=True)
	delivered_qty = fields.Float(compute="_compute_qty", string="Delivered Quantity", help="Delivered quantity of the product", digits=(6, 2), default=0)
	cancelled_qty = fields.Float(compute="_compute_qty", string="cancelled Quantity", help="Cancelled quantity tax of the product", digits=(6, 2), default=0)

	@api.onchange('product_id')
	def onchange_product_id(self):
		if self.product_id:
			self.update({'unit_price': self.product_id.sale_price, 'quantity': 1.0, 'uom_id': self.product_id.uom_id})
		else:
			self.update({'unit_price': ''})

	@api.depends('quantity', 'unit_price')
	def _compute_subtotal(self):
		for orderline in self:
			orderline.subtotal_without_tax = orderline.quantity * orderline.unit_price


	@api.depends('stock_move_ids')
	def _compute_qty(self):
		for orderline in self:
			orderline.delivered_qty = sum(orderline.stock_move_ids.search([('sale_line_id', '=', orderline.id), ('state', '=', 'Done')]).mapped('qty_done'))
			orderline.cancelled_qty = sum(orderline.stock_move_ids.search([('sale_line_id', '=', orderline.id), ('state', '=', 'Cancelled')]).mapped('qty_done'))

			# for move in orderline.stock_move_ids:
			# 	if move.state == 'Done':
			# 		orderline.delivered_qty += move.qty_done
			# 	elif move.state == 'Cancelled':
			# 		orderline.cancelled_qty += move.qty_done
