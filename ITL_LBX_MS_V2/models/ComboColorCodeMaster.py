from odoo import models, fields, api, _


class LbxCoomaster(models.Model):
    _name = "combo_color_code_master"
    _description = "Combo Color Code Master"
    _rec_name = 'combo_color_code'


    combo_color_code = fields.Char (string = 'Combo Color Code')
    combo_color_code_name = fields.Char (string = 'Combo Color Code Name')