# REQUIREMENT 19 ----------------------------------------------------------------------

from odoo import api, models, fields
from odoo.fields import Command
from odoo.exceptions import ValidationError

class ValidateStockPicking(models.TransientModel):

	_name = 'validate.partial.stock.picking'
	_decription = 'Confirm and Validate partial stock picking'

	validate_percentage = fields.Float(string="Percentage", help="Percentage of the stock you want to validate.")
	
	def action_validate_partial_picking(self):
		if self.validate_percentage >= 100:
			raise ValidationError('Percentage can not be 100% or more.')

		sale_order = self.env['sale.order'].browse(self._context.get('active_id', []))
		sale_order.action_confirm()

		# for picking in sale_order.picking_ids:
		for move in sale_order.picking_ids.move_ids:
			move.quantity = (move.product_uom_qty * self.validate_percentage) / 100
		res = sale_order.picking_ids.button_validate()
		# picking._action_done()
		return res
