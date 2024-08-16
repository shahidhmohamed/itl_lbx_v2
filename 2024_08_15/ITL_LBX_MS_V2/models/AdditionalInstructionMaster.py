from odoo import models, fields

class AdditionalIns(models.Model):
    _name = "additional_instruction_master"
    _rec_name = 'additional_ins'

    additional_ins = fields.Char(string='Additional Instruction')
    additional_ins_name = fields.Char(string='Additional Instruction Name')