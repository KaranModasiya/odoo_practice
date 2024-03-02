from odoo import fields, models

class ProductCategory(models.Model):

	_name = 'product.category.ept'
	_description = 'Product Categories'

	name = fields.Char(string="Category Name", help="Name of the product category")
	parent_id = fields.Many2one(comodel_name="product.category.ept", string="Parent Category", help="Parent category of the product category")
	child_ids = fields.One2many(comodel_name="product.category.ept", inverse_name="parent_id", string="Child Category", help="Child category of the product category")
