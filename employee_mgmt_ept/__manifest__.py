{
	'name': 'Employee Management EPT',
	'version': '1.0',
	'author': 'Emipro Technologies',
	'website': 'http://emiprotechnologies.com',
	'description': """
	This module is for Employee management demo.
	""",
	'depends': [],
	'data': [
		'security/employee_security.xml',
		'security/ir.model.access.csv',
		'views/employee_department_views.xml',
		'views/employee_department_shift_views.xml',
		'views/employee_views.xml',
		'views/employee_leave_views.xml',
		'views/employee_mgmt_menus.xml',
	],
}
