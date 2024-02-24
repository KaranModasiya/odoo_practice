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
	sale_order_id = fields.Many2one(comodel_name="sale.order.ept", string="Order Id", help="Order Id of the stock picking unit")
	purchase_order_id = fields.Many2one(comodel_name="purchase.order.ept", string="Purchase Order Id", help="Prchase order Id of the stock picking unit")
	transaction_type = fields.Selection(selection=[
		('In', 'In'),
		('Out', 'Out'),
		], string="Transation Type", help="Transation type of the stock picking unit")
	move_ids = fields.One2many(comodel_name="stock.move.ept", inverse_name="picking_id", string="Purchase Order Id", help="Prchase order Id of the stock picking unit")
	transaction_date = fields.Date(string="Transaction Date", help="Transaction date of the stock picking unit", default=fields.Date.today())
	back_order_id = fields.Many2one(comodel_name="stock.picking.ept", string="Backorder", help="Backorder of the stock picking")

	@api.model
	def create(self, vals):
		if vals['transaction_type'] == 'In':
			vals.update({'name': self.env['ir.sequence'].next_by_code('stock.picking.ept.in')})
		elif vals['transaction_type'] == 'Out':
			vals.update({'name': self.env['ir.sequence'].next_by_code('stock.picking.ept.out')})
		return super().create(vals)

	# button actions

	def action_validate_button(self):
		"""
		Check done quantity of stock moves and if nessacery, create a backorder.
		:return:  None
		"""

		# if all(move.qty_done == 0 for move in self.move_ids):
		# 	raise ValidationError('No products are processed, cannot complete the transaction')

		if set(self.move_ids.mapped('qty_done')) == {0}:
			raise ValidationError('No products are processed, cannot complete the transaction')

		# if not all(move.qty_done <= move.qty_to_deliver for move in self.move_ids):
		# 	raise ValidationError('Done quantity is higher than demand.')

		# if all(move.qty_done == move.qty_to_deliver for move in self.move_ids):
		# 	self.move_ids.state = 'Done'
		# 	self.state = 'Done'
		# else:

		back_order_moves = []
		for move in self.move_ids:
			# create a backorder if delivered/done qty is less than demand
			# if done qty is given more than demand stock move will be counted as done but no backorder will be created
			if move.qty_to_deliver > move.qty_done:
				back_order_moves.append(Command.create({
					'name': move.name,
					'product_id': move.product_id.id,
					'uom_id': move.uom_id.id,
					'source_location_id': move.source_location_id.id,
					'destination_location_id': move.destination_location_id.id,
					'qty_to_deliver': move.qty_to_deliver - move.qty_done,
					'sale_line_id': move.sale_line_id.id,
					'purchase_line_id': move.purchase_line_id.id,
					}))

				# keeping state to draft if done quantity is 0
				if move.qty_done == 0:
					# if we want to unlink stock move from stock picking
					move.picking_id = ''

					# if we want to delete the record
					# move.unlink()
				else:
					move.state = 'Done'

		self.state = 'Done'

		# if any new stock moves are generated then back order will be created
		if len(back_order_moves):
			back_order = self.copy({'back_order_id': self.id, 'move_ids': back_order_moves})

	def action_cancel_button(self):
		# for rec in self.move_ids:
		# 	rec.qty_done = rec.qty_to_deliver
		# 	rec.state = 'Cancelled'
		self.move_ids.qty_done = self.move_ids.qty_to_deliver
		self.move_ids.state = 'Cancelled'
		self.state = 'Cancelled'
