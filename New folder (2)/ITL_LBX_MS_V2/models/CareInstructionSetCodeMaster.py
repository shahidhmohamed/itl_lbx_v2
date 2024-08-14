from odoo import models, fields

class CareInstructionSetCode(models.Model):
    _name = "care_instruction_set_code_master"
    _rec_name = "care_instruction_set_code"

    care_instruction_set_code = fields.Char(string='Care Instruction Set Code')
    care_instruction_set_code_2 = fields.Char(string='Care Instruction Set Code')