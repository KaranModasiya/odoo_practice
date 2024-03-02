from odoo import fields, models, api


class Product(models.Model):

	_name = 'product.ept'
	_description = 'Product Information'

	name = fields.Char(string="Product Name", help="Name of the product", required=True)
	sku = fields.Char(string="SKU", help="Stock Keeping Unit of the product", required=True)
	weight = fields.Float(string="Weight", help="Wegiht of the product", digits=(0, 2))
	length = fields.Float(string="Length", help="Length of the product", digits=(0, 2))
	width = fields.Float(string="Width", help="Width of the product", digits=(0, 2))
	volume = fields.Float(string="Volume", help="Volume of the product", digits=(0, 2))
	barcode = fields.Char(string="Barcode", help="Barcode of the product")
	product_type = fields.Selection(selection=[
		('Storable', 'Storable'), ('Consumable', 'Consumable'), ('Service', 'Service')
		], string="Product Type", help="Type of the product")
	sale_price = fields.Float(string="Sell Price", help="Selling price of the product", digits=(0, 2), default=1)
	cost_price = fields.Float(string="Cost Price", help="Cost price of the product", digits=(0, 2), default=1)
	category_id = fields.Many2one(comodel_name="product.category.ept", string="Product Category", help="Category of the product")
	uom_id = fields.Many2one(comodel_name="product.uom.ept", string="UOM", help="Unit of Measure of the product")
	description = fields.Text(string="Description", help="Description of the product")
	product_stock = fields.Float(compute="_compute_stock", string="Product Stock", help="Stock of the product", digits=(0, 2), store=False)
	parent_ids = fields.Many2many(comodel_name="product.category.ept", compute='_compute_parent_ids', string="parent id", help="parent id many2many")
	tax_ids = fields.Many2many(comodel_name="account.tax.ept", string="Customer Taxes", help="Tax applied on the product")


	def _compute_stock(self):
		"""
		computes available stock of the product.
		:return: None
		"""
		location = self.env.context.get('location')
		stock_location_ids = [location] if location else self.env['stock.warehouse.ept'].search([]).stock_location_id.ids
		move = self.env['stock.move.ept']

		for product in self:
			incoming = sum(move.search([('destination_location_id', 'in', stock_location_ids), ('product_id', '=', product.id), ('state', '=', 'Done')]).mapped('qty_done'))
			outgoing = sum(move.search([('source_location_id', 'in', stock_location_ids), ('product_id', '=', product.id), ('state', '=', 'Done')]).mapped('qty_done'))

			product.product_stock = incoming - outgoing


	@property
	def action_update_stock_button(self):
		return self.env['ir.actions.act_window']._for_xml_id('sale_ept.product_stock_update_wizard_action')


	@api.depends('category_id')
	def _compute_parent_ids(self):
		for rec in self:
			rec.parent_ids = rec.find_childs(rec.category_id)


	def find_childs(self, category):
		if category.child_ids:
			res = category
			for child in category.child_ids:
				res = res + self.find_childs(child)
			return res
		else:
			return category
