{
	'name': 'Sale Management EPT',
	'version': '1.0',
	'author': 'Emipro Technologies',
	'website': 'https://emiprotechnologies.com',
	'description': """
	This module is for Sale management demo.
	""",
	'depends': ['res_localization_ept'],
	'data': [
		'security/sale_security.xml',
		'security/ir.model.access.csv',

		'data/ir_sequence.xml',

		'views/product_category_views.xml',
		'views/product_uom_category_views.xml',
		'views/product_uom_views.xml',
		'wizard/product_stock_update_wizard_views.xml',
		'views/product_views.xml',
		'views/res_partner_views.xml',
		'views/sale_order_views.xml',
		'views/crm_team_views.xml',
		'views/crm_lead_views.xml',
		'views/stock_warehouse_views.xml',
		'views/stock_location_views.xml',
		'views/stock_picking_views.xml',
		'views/stock_move_views.xml',
		'views/purchase_order_views.xml',
		'views/stock_inventory_views.xml',
		'views/account_tax_views.xml',
		'views/sale_ept_menus.xml',

		'data/sale_demo.xml',
	],
	'application': True,
}
