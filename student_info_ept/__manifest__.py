{
	'name': 'Student Info EPT',
	'version': '1.0',
	'author': 'Emipro Technologies',
	'website': 'http://emiprotechnologies.com',
	'description': """
	This module is for Student information evaluation.
	""",
	'depends': ['sales_team'],
	'data': [
		'security/ir.model.access.csv',
		'views/student_views.xml',
		'views/course_views.xml',
		'views/student_menus.xml',
	],
}
