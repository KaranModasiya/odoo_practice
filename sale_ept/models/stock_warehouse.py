from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.fields import Command

class StockWarehouse(models.Model):

	_name = 'stock.warehouse.ept'
	_description = 'Stock Warehouse'

	name = fields.Char(string="Warehouse Name", help="Name of the warehouse", required=True)
	short_code = fields.Char(string="Warehouse Shortcode", help="Shortcode of the warehouse", required=True)
	address_id = fields.Many2one(comodel_name="res.partner.ept", string="Warehouse Manager", help="Manager of the warehouse")
	stock_location_id = fields.Many2one(comodel_name="stock.location.ept", string="Stock Location", help="Stock location of the warehouse")
	view_location_id = fields.Many2one(comodel_name="stock.location.ept", string="View Location", help="View location of the warehouse")

	@api.model
	def create(self, vals):
		location = self.env['stock.location.ept']
		# if not vals['view_location_id']:
		vals['view_location_id'] = location.create({
			'name': "View Location - " + vals['short_code'],
			'location_type': 'View',
			}).id
		# if not vals['stock_location_id']:
		vals['stock_location_id'] = location.create({
			'name': "Internal Location - " + vals['short_code'],
			'location_type': 'Internal',
			'parent_id': vals['view_location_id'],
			}).id
		return super(StockWarehouse, self).create(vals)


