from odoo import api, models, fields
from odoo.fields import Command

class SaleOrder(models.Model):
	_inherit = 'sale.order'

	# REQUIREMENT 15 ----------------------------------------------------------------------
	crm_lead_ept_id = fields.Many2one(comodel_name="crm.lead", string="Lead", domain="[('type', '=', 'lead')]")


	# REQUIREMENT 16 ----------------------------------------------------------------------
	def action_confirm(self):
		self.order_line.create({
			'order_id': self.id,
			'product_id': self.env.ref('sale_extended.product_shipping_charge').id,
			'sequence': 999,
			})
		return super().action_confirm()


	# REQUIREMENT 17 ----------------------------------------------------------------------
	def action_manage_deposits(self):
		for orderline in self.order_line:
			deposit_list = []  # list of product deposits
			orderline.product_id.deposit_product_id and deposit_list.append((orderline.product_id.deposit_product_id, orderline.product_id.deposit_product_qty))
			orderline.product_id.deposit_product_id2 and deposit_list.append((orderline.product_id.deposit_product_id2, orderline.product_id.deposit_product_qty2))

			for deposit in deposit_list:  # deopsit = (deposit product, deposit qty)
				child_deposit_line = orderline.child_ids.filtered_domain([('product_id', '=', deposit[0].id)])
				if not child_deposit_line:
					self.order_line.create({
						'order_id': self.id,
						'deposit_orderline_id': orderline.id,
						'product_id': deposit[0].id,
						'product_uom_qty': deposit[1] * orderline.product_uom_qty,
						'sequence': (orderline.sequence + 1),
						})
				else:
					child_deposit_line.product_uom_qty = deposit[1] * orderline.product_uom_qty


	# REQUIREMENT 18 ----------------------------------------------------------------------
	def action_reserved_orderlines(self):
		products = self.order_line.product_id.ids
		
		# sale order list excluding self, whare stock moves are reserved for products in orderline
		saleorder = self.env['stock.move'].search([('picking_id.sale_id', '!=', self.id), ('state', 'in', ('assigned', 'partially_available'))]).picking_id.sale_id

		# filtering orderlines whare products are from list and product type isn't service
		orderline = saleorder.order_line.filtered_domain([('product_id', 'in', products), ('product_id.detailed_type', '!=', 'service')]).ids

		action = self.env['ir.actions.act_window']._for_xml_id('sale_extended.action_sale_order_line')
		action['domain'] = [('id', 'in', orderline)]
		return action


	# REQUIREMENT 19 ----------------------------------------------------------------------
	def action_confirm_and_validate(self):
		return self.env['ir.actions.act_window']._for_xml_id("sale_extended.validate_partial_stock_picking_wizard_action")


	# REQUIREMENT 20 ----------------------------------------------------------------------
	is_all_picking_competed = fields.Boolean(string="Completed?", help="Is this order is fully completed?", compute="_compute_picking_completed", search="_search_completed_order")
	def _compute_picking_completed(self):
		for order in self:
			order.is_all_picking_competed = True if order.picking_ids and not order.picking_ids.filtered_domain([('state', 'in', ('draft', 'waiting', 'confirmed', 'assigned'))]) else False


	def _search_completed_order(self, operator, value):
		self._cr.execute("""
			select so.id from sale_order so 
			where exists(select 1 from stock_picking picking where picking.sale_id=so.id 
						group by picking.sale_id 
						having count (*)=sum(case when picking.state in('done','cancel') then 1 else 0 end));""")
		res = self._cr.fetchall()
		if not res:
			return [(0, '=', 1)]
		return [('id', 'in' if value else 'not in', [r[0] for r in res])]


	# REQUIREMENT 21 ----------------------------------------------------------------------
	total_profit_percentage = fields.Float(string="Profit Margin Percentage",
	                                       help="Total average profit margin percentage of the order",
	                                       compute="_compute_profit")
	total_profit_value = fields.Float(string="Total Profit", help="Total Profit value of the order",
	                                  compute="_compute_profit")

	@api.depends('order_line')
	def _compute_profit(self):
		for order in self:
			order.total_profit_value = order.order_line and sum(order.order_line.mapped('profit_value')) or 0
			# order.total_profit_percentage = order.order_line and sum(order.order_line.mapped('profit_margin_percentage')) / len(order.order_line) or 0
			sale = sum(order.order_line.mapped('price_unit'))
			cost = sum(order.order_line.mapped('product_id.standard_price'))
			order.total_profit_percentage = order.order_line and ((sale - cost) * 100) / sale


	# REQUIREMENT 22 ----------------------------------------------------------------------
	product_template_ids = fields.Many2many('product.template', string="Product Templates", help="Product templates with it's varients")

	@api.onchange('product_template_ids')
	def _onchange_product_template(self):
		orderlines = []
		variants = self.product_template_ids.product_variant_ids
		if self.product_template_ids:
			for variant in variants._origin:
				if variant.id not in self.order_line.product_id.ids and variant.with_context(warehouse=self.warehouse_id.id).qty_available >= 1:
					# if stock.search([('product_id', '=', variant._origin.id), ('warehouse_id', '=', self.warehouse_id.id), ('quantity', '>', 0)]):
					orderlines.append(Command.create({
						# 'order_id': self._origin.id or self.id,
						'product_id': variant.id,
						'product_uom_qty': 1,
						'manually_created': True,
						}))
			if orderlines:
				self.update({'order_line': orderlines})

		if not orderlines:
			to_unlink = self.order_line.filtered_domain([('product_id', 'not in', variants.ids), ('manually_created', '=', True)])
			if to_unlink:
				self.order_line = [Command.unlink(unlink_id.id) for unlink_id in to_unlink]
