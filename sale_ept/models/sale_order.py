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
		('Done', 'Done'),
		('Cancelled', 'Cancelled')
		], string="Status", help="Status of the order", default="Draft")
	total_weight = fields.Float(compute="_compute_total", string="Total Weight", help="Total weight of the order", digits=(6, 2), default=0)
	total_volume = fields.Float(compute="_compute_total", string="Total Volume", help="Total volume of the order", digits=(6, 2), default=0)
	order_total = fields.Float(compute="_compute_order_total", string="Order Total", help="Total amount to pay for the order", digits=(6, 2), default=0, store=True)
	lead_id = fields.Many2one(comodel_name="crm.lead.ept", string="CRM Lead", help="CRM lead of the order")
	warehouse_id = fields.Many2one(comodel_name="stock.warehouse.ept", string="Warehouse", help="Warehouse of the order")
	picking_ids = fields.One2many(comodel_name="stock.picking.ept", inverse_name="sale_order_id", string="Stock Picking", help="Stock pickings of the order", readonly=True)


	# create method override
	@api.model
	def create(self, vals):
		vals['name'] = self.env['ir.sequence'].next_by_code('sale.order.ept')
		return super(SaleOrder, self).create(vals)


	# computing total weight and volume
	@api.depends('order_line_ids')
	def _compute_total(self):
		for order in self:
			for orderline in order.order_line_ids:
				order.total_weight += orderline.quantity * orderline.product_id.weight
				order.total_volume += orderline.quantity * orderline.product_id.volume
			# order.total_weight = sum(orderline.quantity * orderline.product_id.weight for orderline in order.order_line_ids)
			# order.total_volume = sum(orderline.quantity * orderline.product_id.volume for orderline in order.order_line_ids)


	# computing order total amount
	@api.depends('order_line_ids')
	def _compute_order_total(self):
		"""
		computing order total amount
		:return: None
		"""

		for rec in self:
			rec.order_total = sum(rec.order_line_ids.mapped('subtotal_without_tax'))


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
		if self.order_line_ids:
			# checking if there is any location of customer typw
			customer_location = self.env['stock.location.ept'].search([('location_type', '=', 'Customer')], limit=1)
			if customer_location:
				stock_moves = []

				# changing order lines state to confirm and creating stock moves list for each orderline
				for line in self.order_line_ids:
					# creating stock move
					stock_moves.append(Command.create({
						'name': f"{line.product_id.name} - {self.warehouse_id.stock_location_id.name} -> {customer_location.name}",
						'product_id': line.product_id.id,
						'uom_id': line.uom_id.id,
						'qty_to_deliver': line.quantity,
						'qty_done': 0,
						'sale_line_id': line.id,
						'state': 'Draft',
						'source_location_id': self.warehouse_id.stock_location_id.id,
						'destination_location_id': customer_location.id,
						}))
					line.state = 'Confirmed'

				# generating stock picking record
				stock_pick = self.env['stock.picking.ept'].create({
					'partner_id': self.partner_shipping_id.id,
					'transaction_type': 'Out',
					'move_ids': stock_moves,
					'sale_order_id': self.id,
					})

				# changing sale order state to confirm
				self.state = 'Confirmed'
			else:
				raise ValidationError("System couldn't find Customer location, confirm operation cannot be completed")
		else:
			raise ValidationError("Please add some products to confirm order.")
