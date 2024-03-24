from odoo import api, models, fields
from odoo.fields import Command
from odoo.exceptions import ValidationError

class Purchaseline(models.Model):
	_inherit = 'purchase.order.line'

	# REQUIREMENT 24 ----------------------------------------------------------------------
	history_unit_price = fields.Float(string="Last Price", help="Last price of the product for the partner.",
									  compute="_compute_history_unit_price", store=True)

	@api.depends('product_id', 'order_id.partner_id')
	def _compute_history_unit_price(self):
		for line in self:
			line.history_unit_price = 0
			if line.product_id:
				# query = f"""select po.id from purchase_order po
				# 			where exists(select 1 from purchase_order_line pol
				# 						 where pol.order_id=po.id and state in ('done', 'purchase') and product_id={line.product_id.id})
				# 			and partner_id={line.order_partner_id.id}"""
				#
				# query += " and date_approve<'{line.order_id.date_order}' order by date_approve desc;" if state in ('sale', 'cancel') else " order by id desc"
				# self._cr.execute(query)
				# previous_orders = self.order_id.browse(r[0] for r in self._cr.fetchall())

				domain = [('product_id', '=', line.product_id.id), ('state', 'in', ('done', 'purchase')),
				          ('partner_id', '=', line.order_id.partner_id.id)]
				if line.state in ('done', 'purchase'):
					domain.append(('order_id.date_approve', '<', line.order_id.date_order))
					previous_orders = self.search(domain).order_id.sorted(key='date_approve', reverse=True)
				else:
					previous_orders = self.search(domain).order_id.sorted(key='id', reverse=True)

				last_order = previous_orders and previous_orders[0] or False
				line.history_unit_price = last_order and last_order.order_line.filtered(
					lambda sale: sale.product_id == line.product_id)[-1].price_unit or 0
