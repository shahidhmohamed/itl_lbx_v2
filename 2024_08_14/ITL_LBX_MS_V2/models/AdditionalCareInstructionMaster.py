from odoo import models, fields, api, _


class LbxCoomaster(models.Model):
    _name = "additional_care_instruction"
    _description = "Additional Care Instruction"
    _rec_name = 'additional_care_instruction'


    additional_care_instruction = fields.Char (string = 'Additional Care Instruction')
    additional_care_instruction_name = fields.Char (string = 'Additional Care Instruction Name')