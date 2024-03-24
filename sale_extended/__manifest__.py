
{
	'name': 'Sale Extended EPT',
	'version': '1.0',
	'author': 'Emipro Technologies',
	'website': 'https://emiprotechnologies.com',
	'description': """
	This module is Extension of sale.
	""",
	'depends': ['sale_crm'],
	'data': [
		'security/ir.model.access.csv',
		'data/data.xml',
		'views/sale_order_extended_views.xml',
		'views/purchase_order_views.xml',
		'views/product_views.xml',
		'views/sale_order_line_views.xml',
		'wizard/views_validate_partial_stock_picking_wizard.xml',
		'wizard/record_cancellation_views.xml',
		'wizard/merge_sale_order_wizard_views.xml',
		]
}
