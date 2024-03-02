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
	subtotal_with_tax = fields.Float(compute="_compute_subtotal_with_tax", string="Subtotal With Tax", help="Subtotal with tax of the product", digits=(6, 2), store=True)
	stock_move_ids = fields.One2many(comodel_name="stock.move.ept", inverse_name="sale_line_id", string="Stock Moves", help="Stock moves of the orderline", readonly=True)
	delivered_qty = fields.Float(compute="_compute_qty", string="Delivered Quantity", help="Delivered quantity of the product", digits=(6, 2))
	cancelled_qty = fields.Float(compute="_compute_qty", string="cancelled Quantity", help="Cancelled quantity of the product", digits=(6, 2))
	warehouse_id = fields.Many2one(comodel_name="stock.warehouse.ept", string="Warehouse", help="Warehouse for picking the product")
	tax_ids = fields.Many2many(comodel_name="account.tax.ept", string="Tax", help="Tax applied on the product")
	pending_qty = fields.Float(compute="_compute_qty", string="Pending Quantity", help="Pending quantity of the product", digits=(6, 2))


	@api.onchange('product_id')
	def onchange_product_id(self):
		if self.product_id:
			self.update({'unit_price': self.product_id.sale_price, 'quantity': 1.0, 'uom_id': self.product_id.uom_id, 'tax_ids': self.product_id.tax_ids})
		else:
			self.update({'unit_price': ''})


	# computing orderline subtotal without tax
	@api.depends('quantity', 'unit_price')
	def _compute_subtotal(self):
		for orderline in self:
			orderline.subtotal_without_tax = orderline.quantity * orderline.unit_price


	# computing orderline subtotal with tax
	@api.depends('product_id', 'quantity', 'unit_price', 'tax_ids')
	def _compute_subtotal_with_tax(self):
		for orderline in self:
			tax_amount = 0
			if orderline.tax_ids:
				for tax in orderline.tax_ids:
					if tax.tax_amount_type == 'Percentage':
						tax_amount += (orderline.quantity * orderline.unit_price * tax.tax_value) / 100
					else:
						tax_amount += tax.tax_value
			orderline.subtotal_with_tax = orderline.subtotal_without_tax + tax_amount


	@api.depends('stock_move_ids')
	def _compute_qty(self):
		for orderline in self:
			delivered = sum(orderline.stock_move_ids.filtered_domain([('state', '=', 'Done')]).mapped('qty_done'))
			cancelled = sum(orderline.stock_move_ids.filtered_domain([('state', '=', 'Cancelled')]).mapped('qty_done'))

			orderline.delivered_qty = delivered
			orderline.cancelled_qty = cancelled
			orderline.pending_qty = orderline.quantity - (delivered + cancelled)

