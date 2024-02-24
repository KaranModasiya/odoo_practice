from odoo import fields, models, api
from odoo.exceptions import ValidationError
from odoo.fields import Command

class StockLocation(models.Model):

	_name = 'stock.location.ept'
	_description = 'Stock Location'

	name = fields.Char(string="Name", help="Name of the stock location", required=True)
	parent_id = fields.Many2one(comodel_name="stock.location.ept", string="Parent", help="Parent of the stock location")
	location_type = fields.Selection(selection=[
		('Vendor', 'Vendor'),
		('Customer', 'Customer'),
		('Internal', 'Internal'),
		('Inventory Loss', 'Inventory Loss'),
		('Production', 'Production'),
		('Transit', 'Transit'),
		('View', 'View'),
		], string="Type", help="Type of the stock location")
	is_scrap_location = fields.Boolean(string="Is Scrap Location?", help="Is it scrap location?", defualt=False)
