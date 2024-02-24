from odoo import fields, models

class ProductUomCategory(models.Model):

	_name = 'product.uom.category.ept'
	_description = 'Product Unit of Measure Category'

	name = fields.Char(string="Category Name", help="Name of the UOM category")
	uom_ids = fields.One2many(comodel_name="product.uom.ept",inverse_name="uom_category_id", string="Category Name", help="Name of the UOM category")
