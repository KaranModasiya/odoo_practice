from odoo import fields, models

class ProductUom(models.Model):

	_name = 'product.uom.ept'
	_description = 'Product Unit of Measure'

	name = fields.Char(string="UOM", help="Name of the Unit of Measure")
	uom_category_id = fields.Many2one(comodel_name="product.uom.category.ept", string="UOM Category", help="Category of the UOM")
