from odoo import models, fields

class seasonMaster(models.Model):
    _name = "seson_master"
    _rec_name = "season"

    season = fields.Char(string='Season')
    season_name = fields.Char(string='Season Name')