from odoo import models, fields

class Student(models.Model):

	_name = 'student.ept'
	_description = 'Student EPT'

	name = fields.Char(string="Name", help="Name of the student", required=True)
	std_class = fields.Char(string="Class", help="Class of the student", required=True)
	date_of_birth = fields.Date(string="Birthdate", help="Birthdate of the student", required=True)
	course_ids = fields.Many2many(comodel_name="course.ept", string="Course", help="Courses in which student is enrolled")
