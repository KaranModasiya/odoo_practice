from odoo import fields, models

class ProductCategory(models.Model):

	_name = 'product.category.ept'
	_description = 'Product Categories'

	name = fields.Char(string="Category Name", help="Name of the product category")
	parent_id = fields.Many2one(comodel_name="product.category.ept", string="Parent Category", help="Parent category of the product category")
