from odoo import api, models, fields
from odoo.fields import Command
from odoo.exceptions import ValidationError

class SaleOrderLine(models.Model):
	_inherit = 'sale.order.line'

	# REQUIREMENT 17 ----------------------------------------------------------------------
	deposit_orderline_id = fields.Many2one("sale.order.line", string="Deposit line", help="Deposit orderline for order", ondelete="cascade")
	child_ids = fields.One2many("sale.order.line", inverse_name="deposit_orderline_id", string="Deposit child line", help="Deposit child orderline for order")

	# REQUIREMENT 21 ----------------------------------------------------------------------
	cost_price = fields.Float(string="Cost Price", help="Cost price of the product", compute="_compute_profit", store=True)
	sale_price = fields.Float(string="Sale Price", help="Cost price of the product", compute="_compute_profit", store=True)
	profit_value = fields.Float(string="Profit", help="Profit of the orderline", compute="_compute_profit")
	profit_margin_percentage = fields.Float(string="Profit Margin(%)", help="Profit Margin of the orderline in percentage", compute="_compute_profit")

	@api.depends('product_id', 'product_uom_qty', 'product_uom')
	def _compute_profit(self):
		for order_line in self:
			if order_line.product_id:
				if not order_line._origin.cost_price or order_line._origin.product_id != order_line.product_id:
					order_line._origin.cost_price = order_line.cost_price = order_line.product_id.standard_price
				if not order_line._origin.sale_price or order_line._origin.product_id != order_line.product_id:
					order_line._origin.sale_price = order_line.sale_price = order_line.price_unit

				order_line.profit_value = ((order_line.sale_price or order_line._origin.sale_price) - (order_line.cost_price or order_line._origin.cost_price)) * order_line.product_uom_qty
				order_line.profit_margin_percentage = (((order_line.sale_price or order_line._origin.sale_price) - (order_line.cost_price or order_line._origin.cost_price)) * 100) / ((order_line.sale_price or order_line._origin.sale_price) or 1)
			else:
				order_line.cost_price = order_line.sale_price = order_line.profit_value = order_line.profit_margin_percentage = 0


	# REQUIREMENT 22 ----------------------------------------------------------------------
	manually_created = fields.Boolean(string="Manual created?")


	# REQUIREMENT 23 ----------------------------------------------------------------------
	warehouse_ept_id = fields.Many2one("stock.warehouse", string="Warehouse", help="warehouse for the sale orderline")

	def _prepare_procurement_values(self, group_id=False):
		values = super(SaleOrderLine, self)._prepare_procurement_values(group_id)
		if self.warehouse_ept_id:
			values.update({'warehouse_id': self.warehouse_ept_id})
		return values


	# REQUIREMENT 24 ----------------------------------------------------------------------
	history_unit_price = fields.Float(string="Last Price", help="Last price of the product for the partner.", compute="_compute_history_unit_price", store=True)

	@api.depends('product_id', 'order_id.partner_id')
	def _compute_history_unit_price(self):
		for orderline in self:
			orderline.history_unit_price = 0
			if orderline.product_id:
				# query = f"""select so.id from sale_order so
				# 			where exists(select 1 from sale_order_line sol
				# 						 where sol.order_id=so.id and state = 'sale' and product_id={orderline.product_id.id})
				# 			and partner_id={orderline.order_partner_id.id}"""
				#
				# query += " and date_order<'{orderline.order_id.date_order}' order by date_order desc;" if state in ('sale', 'cancel') else " order by id dedc"
				# self._cr.execute(query)
				# previous_orders = self.order_id.browse(r[0] for r in self._cr.fetchall())

				domain = [('product_id', '=', orderline.product_id.id), ('state', '=', 'sale'), ('order_partner_id', '=', orderline.order_id.partner_id.id)]
				if orderline.state in ('sale', 'cancel'):
					domain.append(('order_id.date_order', '<', orderline.order_id.date_order))
					previous_orders = self.search(domain).order_id.sorted(key='date_order', reverse=True)
				else:
					previous_orders = self.search(domain).order_id.sorted(key='id', reverse=True)

				last_order = previous_orders and previous_orders[0] or False
				orderline.history_unit_price = last_order and last_order.order_line.filtered(lambda sale:sale.product_id == orderline.product_id)[-1].price_unit or 0
