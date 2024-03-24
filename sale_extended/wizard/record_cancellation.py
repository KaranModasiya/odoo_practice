# REQUIREMENT 26 ----------------------------------------------------------------------

from odoo import api, models, fields
from odoo.fields import Command
from odoo.exceptions import ValidationError

class RecordCancellation(models.TransientModel):

	_name = 'record.cancellation.ept'
	_decription = 'Record Cancellation'

	sale_order_ids = fields.Many2many('sale.order', string="Sale Orders", help="Sale order records to cancel",
	                                  default=lambda self: self.env[self._context.get('active_model')].browse(self._context.get('active_ids', [])))
	purchase_order_ids = fields.Many2many('purchase.order', string="Purchase Orders",
	                                      help="Purchase order records to cancel",
	                                      default=lambda self: self.env[self._context.get('active_model')].browse(self._context.get('active_ids', [])))
	internal_transfer_ids = fields.Many2many('stock.picking', string="Order Records", help="Order records to cancel",
	                                         default=lambda self: self.env[self._context.get('active_model')].browse(self._context.get('active_ids', [])))


	def action_cancel_records(self):
		records = self.sale_order_ids or self.purchase_order_ids or self.internal_transfer_ids
		states = records.mapped('state')
		if 'cancel' in states or 'sale' in states or 'done' in states or 'purchase' in states:
			raise ValidationError('One of the selected record is either Done or Cancelled.')

		if self.sale_order_ids:
			res = self.sale_order_ids.with_context(disable_cancel_warning=True).action_cancel()
			return self._action_cancel() if res is not True else res
		elif self.purchase_order_ids:
			self.purchase_order_ids.button_cancel()
		elif self.internal_transfer_ids:
			return self.internal_transfer_ids.action_cancel()
