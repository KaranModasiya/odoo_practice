from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.fields import Command

class StockPicking(models.Model):

	_name = 'stock.picking.ept'
	_description = 'Stock Picking Unit'

	name = fields.Char(string="ID", help="ID of the stock picking unit", default='New')
	partner_id = fields.Many2one(comodel_name="res.partner.ept", string="Partner", help="Partner of the stock picking unit")
	state = fields.Selection(selection=[
		('Draft', 'Draft'),
		('Done', 'Done'),
		('Cancelled', 'Cancelled'),
		], string="Status", help="Status of the stock picking unit", default='Draft')
	sale_order_id = fields.Many2one(comodel_name="sale.order.ept", string="Order Id", help="Order Id of the stock picking unit", ondelete="cascade")
	purchase_order_id = fields.Many2one(comodel_name="purchase.order.ept", string="Purchase Order Id", help="Prchase order Id of the stock picking unit", ondelete="cascade")
	transaction_type = fields.Selection(selection=[
		('In', 'In'),
		('Out', 'Out'),
		], string="Transation Type", help="Transation type of the stock picking unit")
	move_ids = fields.One2many(comodel_name="stock.move.ept", inverse_name="picking_id", string="Purchase Order Id", help="Prchase order Id of the stock picking unit")
	transaction_date = fields.Date(string="Transaction Date", help="Transaction date of the stock picking unit", default=fields.Date.today())
	back_order_id = fields.Many2one(comodel_name="stock.picking.ept", string="Backorder", help="Backorder of the stock picking")
	child_backorder_ids = fields.One2many(comodel_name="stock.picking.ept", inverse_name="back_order_id", string="Child Backorder", help="Backorder of the stock picking")
	saleorder_lines_ids = fields.One2many(comodel_name="sale.order.line.ept", compute="_compute_saleorder_lines", string="Saleorder Lines", help="Saleorder lines of the stock picking")


	@api.model
	def create(self, vals):
		if vals['transaction_type'] == 'In':
			vals.update({'name': self.env['ir.sequence'].next_by_code('stock.picking.ept.in')})
		elif vals['transaction_type'] == 'Out':
			vals.update({'name': self.env['ir.sequence'].next_by_code('stock.picking.ept.out')})
		return super().create(vals)


	def _compute_saleorder_lines(self):
		for rec in self:
			rec.saleorder_lines_ids = rec.move_ids.sale_line_id



	# button actions

	# validate button
	def action_validate_button(self):
		"""
		Check done quantity of stock moves and if nessacery, create a backorder.
		:return:  None
		"""

		if not sum(self.move_ids.mapped('qty_done')):
			# in all records, done qty is zero
			raise ValidationError('No products are processed, cannot complete the transaction')

		# if not all(move.qty_done <= move.qty_to_deliver for move in self.move_ids):
		# 	raise ValidationError('Done quantity is higher than demand.')

		if all(self.move_ids.mapped(lambda move: move.qty_done == move.qty_to_deliver)):
			# all products are done
			self.move_ids.state = 'Done'
			self.state = 'Done'
		else:
			back_order = self.copy({'back_order_id': self.id, 'move_ids': []})
			for move in self.move_ids:
				# if done qty is zero then link this stock move record to new stock picking order(back order)
				if not move.qty_done:
					move.picking_id = back_order.id
				elif (move.qty_to_deliver - move.qty_done) > 0:
					move.copy({'qty_to_deliver': move.qty_to_deliver - move.qty_done, 'qty_done': 0, 'picking_id': back_order.id})

			self.move_ids.state = 'Done'
			self.state = 'Done'

	# cancel button
	def action_cancel_button(self):
		for rec in self.move_ids:
			rec.qty_done = rec.qty_to_deliver
			rec.state = 'Cancelled'
		# self.move_ids.qty_done = self.move_ids.qty_to_deliver
		# self.move_ids.state = 'Cancelled'
		self.state = 'Cancelled'
