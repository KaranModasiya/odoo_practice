from odoo import models, fields

class Course(models.Model):

	_name = 'course.ept'
	_description = 'Course EPT'

	name = fields.Char(string="Name", help="Name of the course", required=True)
	student_ids = fields.Many2many(comodel_name="student.ept", string="Student", help="Students who are enrolled in this course")
