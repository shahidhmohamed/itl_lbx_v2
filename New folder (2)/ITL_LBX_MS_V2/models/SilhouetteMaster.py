from odoo import models, fields, api, _


class Silhouettemaster(models.Model):
    _name = "silhouette_master"
    _description = "LBX SILHOUETTE MASTER"
    _rec_name = 'silhouette'


    silhouette = fields.Char (string = 'Silhouette')
    silhouette_name = fields.Char (string = 'Silhouette Name')