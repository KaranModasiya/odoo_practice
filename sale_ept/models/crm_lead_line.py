from odoo import fields, models, api
from odoo.exceptions import ValidationError

class CrmLeadLine(models.Model):

	_name = 'crm.lead.line.ept'
	_description = 'CRM Leadlines'

	product_id = fields.Many2one(comodel_name="product.ept", string="Product Id", help="Product Id of the leadline")
	name = fields.Text(string="Description", help="Description of the leadline")
	expected_sell_qty = fields.Float(string="Expected Sell Quantity", help="Expected sell quantity of the product", default=0)
	uom_id = fields.Many2one(comodel_name="product.uom.ept", string="Product UOM", help="Unit of Measure of the product")
	lead_id = fields.Many2one(comodel_name="crm.lead.ept", string="Lead Id", help="Lead Id of the leadline")

	@api.onchange('product_id')
	def onchange_product_id(self):
		if self.product_id:
			self.name = self.product_id.name
			self.uom_id = self.product_id.uom_id
			self.expected_sell_qty = 1
		else:
			self.name = ''
			self.expected_sell_qty = 0
