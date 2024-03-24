# REQUIREMENT 26 ----------------------------------------------------------------------

from odoo import api, models, fields
from odoo.fields import Command
from odoo.exceptions import ValidationError


class MergeSaleOrder(models.TransientModel):
	_name = 'merge.sale.order.wizard'
	_decription = 'Merge Saleorders'

	merge_options = fields.Selection([
		('merge_create_cancel', 'Merge and Cancel selected sale orders'),
		('merge_create_delete', 'Merge and Delete selected sale orders'),
		('merge_exising_cancel', 'Merge in exisitng sale order and Cancel selected'),
		('merge_exising_delete', 'Merge in exisitng sale order and Delete selected'),
	], default="merge_create_cancel", string="Merge Options", help="Merge options for selected sale orders.")
	sale_order_id = fields.Many2one("sale.order", string="Sale order",
									help="Select sale order to merge selected sale orders in this sale order")
	sale_order_ids = fields.Many2many("sale.order", string="Sale Orders", help="Selected sale orders")


	# for merging selected sale orders
	def action_merge_sale_orders(self):
		order_lines_list = []

		# to append orderline in list
		def append_orderline(orderline):
			order_lines_list.append(Command.create({
				'product_id': order_line.product_id.id,
				'product_uom_qty': order_line.product_uom_qty,
				'product_uom': order_line.product_uom.id,
				'price_unit': order_line.price_unit,
				'tax_id': order_line.tax_id,
				'warehouse_ept_id': order_line.warehouse_ept_id.id,
			}))

		# to check if orderline is already added in list. if not then add in list.
		def check_in_list(orderline):
			for line in order_lines_list:
				if line[2]['product_id'] == order_line.product_id.id and line[2]['product_uom'] == order_line.product_uom.id and line[2]['price_unit'] == order_line.price_unit and line[2]['tax_id'] == order_line.tax_id:
					# if required parameters are same then increase the quantity
					line[2]['product_uom_qty'] += order_line.product_uom_qty
					return
			else:
				# if required parameters are not same then append orderline into list
				append_orderline(order_line)

		# if selected option is to merge and create new sale order.
		if self.merge_options in ('merge_create_cancel', 'merge_create_delete'):
			for order_line in self.sale_order_ids.order_line:
				check_in_list(order_line)

			# create new sale order and add orderline list to order_line
			self.sale_order_ids.create({
				'partner_id': self.sale_order_ids[0].partner_id.id,
				'order_line': order_lines_list
			})

		else:  # if selected option is merge in to one of the selected sale order.
			self.sale_order_ids -= self.sale_order_id

			for order_line in self.sale_order_ids.order_line:
				# filter-out orderlines with the same product as order_line
				orderlines = self.sale_order_id.order_line.filtered_domain([('product_id', '=', order_line.product_id.id)])
				for line in orderlines:
					if order_line.product_uom == line.product_uom and order_line.price_unit == line.price_unit and order_line.tax_id == line.tax_id:
						# if required parameters are same then increase the quantity of exiting order line
						line.product_uom_qty += order_line.product_uom_qty
						break
				else:
					# if required parameters are not same then check if the order line is appended in list or not
					check_in_list(order_line)

			# add new orderlines in existing sale order
			self.sale_order_id.order_line = order_lines_list

		# cancel or delete remaining selected sale orders as per user selected option
		if self.merge_options in ('merge_create_cancel', 'merge_exising_cancel'):
			self.sale_order_ids.state = 'cancel'
		else:
			self.sale_order_ids.unlink()

	@api.model
	def default_get(self, fields):
		active_orders = self.env['sale.order'].browse(self._context.get('active_ids', []))
		if len(active_orders.mapped('partner_id')) != 1:
			raise ValidationError('You can not select orders of more than one customer.')
		elif len(active_orders) == 1:
			raise ValidationError('You neet to select atleast two sale order to merge.')
		if set(active_orders.mapped('state')) != {'draft'}:
			raise ValidationError('You can only select Quotations.')
		res = super(MergeSaleOrder, self).default_get(fields)
		res.update({'sale_order_ids': active_orders})
		return res
