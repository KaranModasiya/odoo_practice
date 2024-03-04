from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.fields import Command


class SaleOrder(models.Model):
	_name = 'sale.order.ept'
	_description = 'Sale Order'

	name = fields.Char(string="Order No.", help="Order number of the order", default='New')
	partner_id = fields.Many2one(comodel_name="res.partner.ept", string="Customer", help="Customer of the order", required=True)
	partner_invoice_id = fields.Many2one(comodel_name="res.partner.ept", string="Invoice Customer", help="Invoice customer of the order")
	partner_shipping_id = fields.Many2one(comodel_name="res.partner.ept", string="Shipping Customer", help="Shipping customer of the order")
	order_date = fields.Date(string="Order Date", help="Order date of the order", default=fields.Date.today())
	order_line_ids = fields.One2many(comodel_name="sale.order.line.ept", inverse_name="order_id", string="Order Lines", help="Order lines of the order")
	saleperson_id = fields.Many2one(comodel_name="res.users", string="Sale Person", help="Sale person of the order")
	state = fields.Selection(selection=[
		('Draft', 'Draft'),
		('Confirmed', 'Confirmed'),
		('Cancelled', 'Cancelled')
		], string="Status", help="Status of the order", default="Draft")
	total_weight = fields.Float(compute="_compute_total", string="Total Weight", help="Total weight of the order", digits=(6, 2))
	total_volume = fields.Float(compute="_compute_total", string="Total Volume", help="Total volume of the order", digits=(6, 2))
	order_total = fields.Float(compute="_compute_order_total", string="Order Total", help="Total amount without tax for the order", digits=(6, 2), store=True)
	lead_id = fields.Many2one(comodel_name="crm.lead.ept", string="CRM Lead", help="CRM lead of the order")
	warehouse_id = fields.Many2one(comodel_name="stock.warehouse.ept", string="Warehouse", help="Warehouse of the order")
	picking_ids = fields.One2many(comodel_name="stock.picking.ept", inverse_name="sale_order_id", string="Stock Picking", help="Stock pickings of the order", readonly=True)
	order_stock_moves = fields.Char(string="Stock Moves", help="Stock moves of the order", compute="_compute_stock_moves")
	total_tax = fields.Float(compute="_compute_total_tax", string="Total Tax", help="Total amount of tax for the order", digits=(6, 2), store=True)
	total_amount = fields.Float(compute="_compute_total_amount", string="Total Amount", help="Total amount to pay with tax for the order", digits=(6, 2), store=True)


	# create method override
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('sale.order.ept')
		return super(SaleOrder, self).create(vals)


	# computing total weight and volume
	def _compute_total(self):
		for order in self:
			order.total_weight = 0
			order.total_volume = 0
			for orderline in order.order_line_ids:
				order.total_weight += orderline.quantity * orderline.product_id.weight
				order.total_volume += orderline.quantity * orderline.product_id.volume


	# computing order total amount without tax
	@api.depends('order_line_ids')
	def _compute_order_total(self):
		"""
		computing total amount  without tax
		:return: None
		"""

		# computing order total amount with tax
		for rec in self:
			rec.order_total = sum(rec.order_line_ids.mapped('subtotal_without_tax'))


	@api.depends('order_line_ids')
	def _compute_total_amount(self):
		for rec in self:
			rec.total_amount = sum(rec.order_line_ids.mapped('subtotal_with_tax'))



	# computing total tax amount
	@api.depends('order_line_ids')
	def _compute_total_tax(self):
		"""
		computing total tax amount
		:return: None
		"""
		for rec in self:
			rec.total_tax = rec.total_amount - rec.order_total


	# setting invoice and shipping address as per partner
	@api.onchange('partner_id')
	def onchange_partner_id(self):
		if self.partner_id:
			invoice = self.partner_id.child_ids.filtered_domain([('address_type', '=', 'Invoice')])
			shipping = self.partner_id.child_ids.filtered_domain([('address_type', '=', 'Shipping')])

			self.partner_invoice_id = invoice and invoice[0] or self.partner_id
			self.partner_shipping_id = shipping and shipping[0] or self.partner_id
		else:
			self.partner_invoice_id = ''
			self.partner_shipping_id = ''


	# button actions
	def action_confirm_order_button(self):
		"""
		To confirm sale order.
		Changes state of sale order record and related sale order lines records to Confirmed.
		Creates stock picking record and stock move records.
		:return: None
		"""
		if not self.order_line_ids:
			raise ValidationError("Please add some products to confirm order.")

		# checking if there is any location of customer type
		customer_location = self.env['stock.location.ept'].search([('location_type', '=', 'Customer')], limit=1)
		if not customer_location:
			raise ValidationError("System couldn't find Customer location, confirm operation cannot be completed")

		warehouse_list = self.order_line_ids.warehouse_id.ids
		self.warehouse_id.id not in warehouse_list and warehouse_list.append(self.warehouse_id.id)

		# generating delivery order for each warehouse in saleorder_line
		for warehouse in self.warehouse_id.browse(warehouse_list):
			if warehouse != self.warehouse_id:
				filtered_lines = self.order_line_ids.filtered_domain([('warehouse_id', '=', warehouse.id)])
			else:
				filtered_lines = self.order_line_ids.filtered_domain(['|', ('warehouse_id', '=', warehouse.id), ('warehouse_id.id', '=', False)])

			# changing order lines state to confirm and creating stock moves list for same warehouse
			if filtered_lines:
				stock_moves = []
				for line in filtered_lines:
					# creating stock move
					stock_moves.append(Command.create({
						'name': f"{line.product_id.name} - {warehouse.stock_location_id.name} -> {customer_location.name}",
						'product_id': line.product_id.id,
						'uom_id': line.uom_id.id,
						'qty_to_deliver': line.quantity,
						'qty_done': 0,
						'sale_line_id': line.id,
						'state': 'Draft',
						'source_location_id': warehouse.stock_location_id.id,
						'destination_location_id': customer_location.id,
						}))
					line.state = 'Confirmed'

				# generating stock picking record for warehouse
				self.env['stock.picking.ept'].create({
					'partner_id': self.partner_shipping_id.id,
					'transaction_type': 'Out',
					'move_ids': stock_moves,
					'sale_order_id': self.id,
					})

		# changing sale order state to confirm
		self.state = 'Confirmed'


	def action_cancel_order_button(self):
		self.state = 'Cancelled'


	def action_view_delivery(self):
		action = self.env['ir.actions.act_window']._for_xml_id("sale_ept.stock_picking_ept_outcoming_action")
		delivery_count = len(self.picking_ids.ids)

		if not delivery_count:
			raise ValidationError('No Records Found')

		if delivery_count > 1:
			action['domain'] = [('sale_order_id', '=', self.id)]
		elif delivery_count == 1:
			action['views'] = [(self.env.ref('sale_ept.view_stock_picking_ept_form').id, 'form')]
			action['res_id'] = self.picking_ids.ids[0]

		return action


	def _compute_stock_moves(self):
		for order in self:
			count = self.env['stock.move.ept'].search_count([('picking_id', 'in', self.picking_ids.ids)])
			if not count:
				order.order_stock_moves = 'No records'
			elif count == 1:
				order.order_stock_moves = str(count) + ' record'
			else:
				order.order_stock_moves = str(count) + ' records'


	def action_view_moves(self):
		action = self.env['ir.actions.act_window']._for_xml_id("sale_ept.stock_move_ept_action")
		delivery_count = len(self.picking_ids.ids)

		if not delivery_count:
			raise ValidationError('No Records Found')
		else:
			action['domain'] = [('picking_id', 'in', self.picking_ids.ids)]

		return action
