from odoo import models, fields, api, _


class SetFiber(models.Model):
    _name = "composition_master"
    _description = "Set fiber details" 
    _rec_name = 'FinalComposition'

    composition_lines = fields.One2many('composition_lines', 'connect', string="composition_lines")
    composition_02_lines = fields.One2many('composition_lines_tab_02', 'connect01', string="composition_lines_02")
    composition_03_lines = fields.One2many('composition_lines_tab_03', 'connect03', string="composition_lines_02")
    composition_04_lines = fields.One2many('composition_lines_tab_04', 'connect04', string="composition_lines_02")
    composition_05_lines = fields.One2many('composition_lines_tab_05', 'connect05', string="composition_lines_02")
    composition_06_lines = fields.One2many('composition_lines_tab_06', 'connect06', string="composition_lines_02")
    composition_07_lines = fields.One2many('composition_lines_tab_07', 'connect07', string="composition_lines_02")
    composition_08_lines = fields.One2many('composition_lines_tab_08', 'connect08', string="composition_lines_02")
    composition_09_lines = fields.One2many('composition_lines_tab_09', 'connect09', string="composition_lines_02")
    composition_010_lines = fields.One2many('composition_lines_tab_010', 'connect010', string="composition_lines_02")
    composition_011_lines = fields.One2many('composition_lines_tab_011', 'connect011', string="composition_lines_02")


    # Final Component
    FinalComposition = fields.Char(string='Composition', compute ='_composition_final', store=True)
    @api.depends(
    'composition_1', 'composition_2', 'composition_3',
    'composition_4', 'composition_5',
    'composition_6', 'composition_8',
    'composition_8', 'composition_9',
    'composition_10'
    )

    def _composition_final(self):
        for record in self:
            composition_info = []  # List to store information for each fiber

            if record.composition_1:
                composition_info.append(f"{record.composition_1}")

            if record.composition_2:
                composition_info.append(f"{record.composition_2}")

            if record.composition_3:
                composition_info.append(f"{record.composition_3}")

            if record.composition_4:
                composition_info.append(f"{record.composition_4}")
                
            if record.composition_5:
                composition_info.append(f"{record.composition_5}")

            if record.composition_6:
                composition_info.append(f"{record.composition_6}")

            if record.composition_7:
                composition_info.append(f"{record.composition_7}")

            if record.composition_8:
                composition_info.append(f"{record.composition_8}")

            if record.composition_9:
                composition_info.append(f"{record.composition_9}")

            if record.composition_10:
                composition_info.append(f"{record.composition_10}")

            # Combine information for all fibers
            record.FinalComposition = ' '.join(composition_info) if composition_info else False


    # component 1
    Component_1 = fields.Many2one('components_master', string='Select Component', store=True)
    Component_1_name = fields.Char(string='Selected Component', related='Component_1.ComponentName', readonly=True, store=True)

    component_1_Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1', store=True)
    component_1_fiber1_name = fields.Char(string='Fiber 1', related='component_1_Fiber1.fibername', readonly=True, store=True)
    component_1_Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    component_1_Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2', store=True)
    component_1_fiber2_name = fields.Char(string='Fiber 2', related='component_1_Fiber2.fibername', readonly=True, store=True)
    component_1_Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    component_1_Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3', store=True)
    component_1_fiber3_name = fields.Char(string='Fiber 3', related='component_1_Fiber3.fibername', readonly=True, store=True)
    component_1_Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    component_1_Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4', store=True)
    component_1_fiber4_name = fields.Char(string='Fiber 4', related='component_1_Fiber4.fibername', readonly=True, store=True)
    component_1_Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    component_1_Fiber5 = fields.Many2one('fiber_master', string='Select Fiber 5', store=True)
    component_1_fiber5_name = fields.Char(string='Fiber 5', related='component_1_Fiber5.fibername', readonly=True, store=True)
    component_1_Fiber5_Percentage = fields.Char(string='Fiber 5 Percentage', store=True)

    component_1_Fiber6 = fields.Many2one('fiber_master', string='Select Fiber 6', store=True)
    component_1_fiber6_name = fields.Char(string='Fiber 6', related='component_1_Fiber6.fibername', readonly=True, store=True)
    component_1_Fiber6_Percentage = fields.Char(string='Fiber 6 Percentage')

    component_1_Fiber7 = fields.Many2one('fiber_master', string='Select Fiber 7', store=True)
    component_1_fiber7_name = fields.Char(string='Fiber 7', related='component_1_Fiber7.fibername', readonly=True, store=True)
    component_1_Fiber7_Percentage = fields.Char(string='Fiber 7 Percentage', store=True)

    component_1_Fiber8 = fields.Many2one('fiber_master', string='Select Fiber 8', store=True)
    component_1_fiber8_name = fields.Char(string='Fiber 8', related='component_1_Fiber8.fibername', readonly=True, store=True)
    component_1_Fiber8_Percentage = fields.Char(string='Fiber 8 Percentage')

    component_1_Fiber9 = fields.Many2one('fiber_master', string='Select Fiber 9', store=True)
    component_1_fiber9_name = fields.Char(string='Fiber 9', related='component_1_Fiber9.fibername', readonly=True, store=True)
    component_1_Fiber9_Percentage = fields.Char(string='Fiber 9 Percentage')

    component_1_Fiber10 = fields.Many2one('fiber_master', string='Select Fiber 10', store=True)
    component_1_fiber10_name = fields.Char(string='Fiber 10', related='component_1_Fiber10.fibername', readonly=True, store=True)
    component_1_Fiber10_Percentage = fields.Char(string='Fiber 10 Percentage')

    composition_1 = fields.Char(string='Component 01' , compute ='_fiber_create_1', store=True)

    

    @api.depends(
    'Component_1', 'component_1_Fiber1', 'component_1_Fiber1_Percentage',
    'component_1_Fiber2', 'component_1_Fiber2_Percentage',
    'component_1_Fiber3', 'component_1_Fiber3_Percentage',
    'component_1_Fiber4', 'component_1_Fiber4_Percentage',
    'component_1_Fiber5', 'component_1_Fiber5_Percentage',
    'component_1_Fiber6', 'component_1_Fiber6_Percentage',
    'component_1_Fiber7', 'component_1_Fiber7_Percentage',
    'component_1_Fiber8', 'component_1_Fiber8_Percentage',
    'component_1_Fiber9', 'component_1_Fiber9_Percentage',
    'component_1_Fiber10', 'component_1_Fiber10_Percentage'
    )

    def _fiber_create_1(self):
        for record in self:
            composition_info = []  # List to store information for each fiber

            if record.Component_1 and record.component_1_Fiber1 and record.component_1_Fiber1_Percentage:
                composition_info.append(f"{record.Component_1.ComponentName}: {record.component_1_Fiber1_Percentage}% {record.component_1_Fiber1.fibername}")

            if record.component_1_Fiber2 and record.component_1_Fiber2_Percentage:
                composition_info.append(f"{record.component_1_Fiber2_Percentage}% {record.component_1_Fiber2.fibername}")

            if record.component_1_Fiber3 and record.component_1_Fiber3_Percentage:
                composition_info.append(f"{record.component_1_Fiber3_Percentage}% {record.component_1_Fiber3.fibername}")

            if record.component_1_Fiber4 and record.component_1_Fiber4_Percentage:
                composition_info.append(f"{record.component_1_Fiber4_Percentage}% {record.component_1_Fiber4.fibername}")
                
            if record.component_1_Fiber5 and record.component_1_Fiber5_Percentage:
                composition_info.append(f"{record.component_1_Fiber5_Percentage}% {record.component_1_Fiber5.fibername}")

            if record.component_1_Fiber6 and record.component_1_Fiber6_Percentage:
                composition_info.append(f"{record.component_1_Fiber6_Percentage}% {record.component_1_Fiber6.fibername}")

            if record.component_1_Fiber7 and record.component_1_Fiber7_Percentage:
                composition_info.append(f"{record.component_1_Fiber7_Percentage}% {record.component_1_Fiber7.fibername}")

            if record.component_1_Fiber8 and record.component_1_Fiber8_Percentage:
                composition_info.append(f"{record.component_1_Fiber8_Percentage}% {record.component_1_Fiber8.fibername}")

            if record.component_1_Fiber9 and record.component_1_Fiber9_Percentage:
                composition_info.append(f"{record.component_1_Fiber9_Percentage}% {record.component_1_Fiber9.fibername}")

            if record.component_1_Fiber10 and record.component_1_Fiber10_Percentage:
                composition_info.append(f"{record.component_1_Fiber10_Percentage}% {record.component_1_Fiber10.fibername}")

            # Combine information for all fibers
            record.composition_1 = ', '.join(composition_info) if composition_info else False


    # component 2
    Component_2 = fields.Many2one('components_master', string='Select Component', store=True)
    Component_2_name = fields.Char(string='Selected Component', related='Component_2.ComponentName', readonly=True, store=True)

    component_2_Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1', store=True)
    component_2_fiber1_name = fields.Char(string='Fiber 1', related='component_2_Fiber1.fibername', readonly=True, store=True)
    component_2_Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    component_2_Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2', store=True)
    component_2_fiber2_name = fields.Char(string='Fiber 2', related='component_2_Fiber2.fibername', readonly=True, store=True)
    component_2_Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    component_2_Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3', store=True)
    component_2_fiber3_name = fields.Char(string='Fiber 3', related='component_2_Fiber3.fibername', readonly=True, store=True)
    component_2_Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    component_2_Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4', store=True)
    component_2_fiber4_name = fields.Char(string='Fiber 4', related='component_2_Fiber4.fibername', readonly=True, store=True)
    component_2_Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    component_2_Fiber5 = fields.Many2one('fiber_master', string='Select Fiber 5', store=True)
    component_2_fiber5_name = fields.Char(string='Fiber 5', related='component_2_Fiber5.fibername', readonly=True, store=True)
    component_2_Fiber5_Percentage = fields.Char(string='Fiber 5 Percentage', store=True)

    component_2_Fiber6 = fields.Many2one('fiber_master', string='Select Fiber 6', store=True)
    component_2_fiber6_name = fields.Char(string='Fiber 6', related='component_2_Fiber6.fibername', readonly=True, store=True)
    component_2_Fiber6_Percentage = fields.Char(string='Fiber 6 Percentage')

    component_2_Fiber7 = fields.Many2one('fiber_master', string='Select Fiber 7', store=True)
    component_2_fiber7_name = fields.Char(string='Fiber 7', related='component_2_Fiber7.fibername', readonly=True, store=True)
    component_2_Fiber7_Percentage = fields.Char(string='Fiber 7 Percentage', store=True)

    component_2_Fiber8 = fields.Many2one('fiber_master', string='Select Fiber 8', store=True)
    component_2_fiber8_name = fields.Char(string='Fiber 8', related='component_2_Fiber8.fibername', readonly=True, store=True)
    component_2_Fiber8_Percentage = fields.Char(string='Fiber 8 Percentage')

    component_2_Fiber9 = fields.Many2one('fiber_master', string='Select Fiber 9', store=True)
    component_2_fiber9_name = fields.Char(string='Fiber 9', related='component_2_Fiber9.fibername', readonly=True, store=True)
    component_2_Fiber9_Percentage = fields.Char(string='Fiber 9 Percentage')

    component_2_Fiber10 = fields.Many2one('fiber_master', string='Select Fiber 10', store=True)
    component_2_fiber10_name = fields.Char(string='Fiber 10', related='component_2_Fiber10.fibername', readonly=True, store=True)
    component_2_Fiber10_Percentage = fields.Char(string='Fiber 10 Percentage')

    composition_2 = fields.Char(string='Component 02', compute ='_fiber_create_2')

    @api.depends(
    'Component_2', 'component_2_Fiber1', 'component_2_Fiber1_Percentage',
    'component_2_Fiber2', 'component_2_Fiber2_Percentage',
    'component_2_Fiber3', 'component_2_Fiber3_Percentage',
    'component_2_Fiber4', 'component_2_Fiber4_Percentage',
    'component_2_Fiber5', 'component_2_Fiber5_Percentage',
    'component_2_Fiber6', 'component_2_Fiber6_Percentage',
    'component_2_Fiber7', 'component_2_Fiber7_Percentage',
    'component_2_Fiber8', 'component_2_Fiber8_Percentage',
    'component_2_Fiber9', 'component_2_Fiber9_Percentage',
    'component_2_Fiber10', 'component_2_Fiber10_Percentage'
    )

    def _fiber_create_2(self):
        for record in self:
            composition_info = []  # List to store information for each fiber

            if record.Component_2 and record.component_2_Fiber1 and record.component_2_Fiber1_Percentage:
                composition_info.append(f"{record.Component_2.ComponentName}: {record.component_2_Fiber1_Percentage}% {record.component_2_Fiber1.fibername}")

            if record.component_2_Fiber2 and record.component_2_Fiber2_Percentage:
                composition_info.append(f"{record.component_2_Fiber2_Percentage}% {record.component_2_Fiber2.fibername}")

            if record.component_2_Fiber3 and record.component_2_Fiber3_Percentage:
                composition_info.append(f"{record.component_2_Fiber3_Percentage}% {record.component_2_Fiber3.fibername}")

            if record.component_2_Fiber4 and record.component_2_Fiber4_Percentage:
                composition_info.append(f"{record.component_2_Fiber4_Percentage}% {record.component_2_Fiber4.fibername}")
                
            if record.component_2_Fiber5 and record.component_2_Fiber5_Percentage:
                composition_info.append(f"{record.component_2_Fiber5_Percentage}% {record.component_2_Fiber5.fibername}")

            if record.component_2_Fiber6 and record.component_2_Fiber6_Percentage:
                composition_info.append(f"{record.component_2_Fiber6_Percentage}% {record.component_2_Fiber6.fibername}")

            if record.component_2_Fiber7 and record.component_2_Fiber7_Percentage:
                composition_info.append(f"{record.component_2_Fiber7_Percentage}% {record.component_2_Fiber7.fibername}")

            if record.component_2_Fiber8 and record.component_2_Fiber8_Percentage:
                composition_info.append(f"{record.component_2_Fiber8_Percentage}% {record.component_2_Fiber8.fibername}")

            if record.component_2_Fiber9 and record.component_2_Fiber9_Percentage:
                composition_info.append(f"{record.component_2_Fiber9_Percentage}% {record.component_2_Fiber9.fibername}")

            if record.component_2_Fiber10 and record.component_2_Fiber10_Percentage:
                composition_info.append(f"{record.component_2_Fiber10_Percentage}% {record.component_2_Fiber10.fibername}")

            # Combine information for all fibers
            record.composition_2 = ', '.join(composition_info) if composition_info else False

    # component 3
    Component_3 = fields.Many2one('components_master', string='Select Component', store=True)
    Component_3_name = fields.Char(string='Selected Component', related='Component_3.ComponentName', readonly=True, store=True)

    component_3_Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1', store=True)
    component_3_fiber1_name = fields.Char(string='Fiber 1', related='component_3_Fiber1.fibername', readonly=True, store=True)
    component_3_Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    component_3_Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2', store=True)
    component_3_fiber2_name = fields.Char(string='Fiber 2', related='component_3_Fiber2.fibername', readonly=True, store=True)
    component_3_Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    component_3_Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3', store=True)
    component_3_fiber3_name = fields.Char(string='Fiber 3', related='component_3_Fiber3.fibername', readonly=True, store=True)
    component_3_Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    component_3_Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4', store=True)
    component_3_fiber4_name = fields.Char(string='Fiber 4', related='component_3_Fiber4.fibername', readonly=True, store=True)
    component_3_Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    component_3_Fiber5 = fields.Many2one('fiber_master', string='Select Fiber 5', store=True)
    component_3_fiber5_name = fields.Char(string='Fiber 5', related='component_3_Fiber5.fibername', readonly=True, store=True)
    component_3_Fiber5_Percentage = fields.Char(string='Fiber 5 Percentage', store=True)

    component_3_Fiber6 = fields.Many2one('fiber_master', string='Select Fiber 6', store=True)
    component_3_fiber6_name = fields.Char(string='Fiber 6', related='component_3_Fiber6.fibername', readonly=True, store=True)
    component_3_Fiber6_Percentage = fields.Char(string='Fiber 6 Percentage')

    component_3_Fiber7 = fields.Many2one('fiber_master', string='Select Fiber 7', store=True)
    component_3_fiber7_name = fields.Char(string='Fiber 7', related='component_3_Fiber7.fibername', readonly=True, store=True)
    component_3_Fiber7_Percentage = fields.Char(string='Fiber 7 Percentage', store=True)

    component_3_Fiber8 = fields.Many2one('fiber_master', string='Select Fiber 8', store=True)
    component_3_fiber8_name = fields.Char(string='Fiber 8', related='component_3_Fiber8.fibername', readonly=True, store=True)
    component_3_Fiber8_Percentage = fields.Char(string='Fiber 8 Percentage')

    component_3_Fiber9 = fields.Many2one('fiber_master', string='Select Fiber 9', store=True)
    component_3_fiber9_name = fields.Char(string='Fiber 9', related='component_3_Fiber9.fibername', readonly=True, store=True)
    component_3_Fiber9_Percentage = fields.Char(string='Fiber 9 Percentage')

    component_3_Fiber10 = fields.Many2one('fiber_master', string='Select Fiber 10', store=True)
    component_3_fiber10_name = fields.Char(string='Fiber 10', related='component_3_Fiber10.fibername', readonly=True, store=True)
    component_3_Fiber10_Percentage = fields.Char(string='Fiber 10 Percentage')

    composition_3 = fields.Char(string='Component 03', compute ='_fiber_create_3')

    

    @api.depends(
    'Component_3', 'component_3_Fiber1', 'component_3_Fiber1_Percentage',
    'component_3_Fiber2', 'component_3_Fiber2_Percentage',
    'component_3_Fiber3', 'component_3_Fiber3_Percentage',
    'component_3_Fiber4', 'component_3_Fiber4_Percentage',
    'component_3_Fiber5', 'component_3_Fiber5_Percentage',
    'component_3_Fiber6', 'component_3_Fiber6_Percentage',
    'component_3_Fiber7', 'component_3_Fiber7_Percentage',
    'component_3_Fiber8', 'component_3_Fiber8_Percentage',
    'component_3_Fiber9', 'component_3_Fiber9_Percentage',
    'component_3_Fiber10', 'component_3_Fiber10_Percentage'
    )

    def _fiber_create_3(self):
        for record in self:
            composition_info = []  # List to store information for each fiber

            if record.Component_3 and record.component_3_Fiber1 and record.component_3_Fiber1_Percentage:
                composition_info.append(f"{record.Component_3.ComponentName}: {record.component_3_Fiber1_Percentage}% {record.component_3_Fiber1.fibername}")

            if record.component_3_Fiber2 and record.component_3_Fiber2_Percentage:
                composition_info.append(f"{record.component_3_Fiber2_Percentage}% {record.component_3_Fiber2.fibername}")

            if record.component_3_Fiber3 and record.component_3_Fiber3_Percentage:
                composition_info.append(f"{record.component_3_Fiber3_Percentage}% {record.component_3_Fiber3.fibername}")

            if record.component_3_Fiber4 and record.component_3_Fiber4_Percentage:
                composition_info.append(f"{record.component_3_Fiber4_Percentage}% {record.component_3_Fiber4.fibername}")
                
            if record.component_3_Fiber5 and record.component_3_Fiber5_Percentage:
                composition_info.append(f"{record.component_3_Fiber5_Percentage}% {record.component_3_Fiber5.fibername}")

            if record.component_3_Fiber6 and record.component_3_Fiber6_Percentage:
                composition_info.append(f"{record.component_3_Fiber6_Percentage}% {record.component_3_Fiber6.fibername}")

            if record.component_3_Fiber7 and record.component_3_Fiber7_Percentage:
                composition_info.append(f"{record.component_3_Fiber7_Percentage}% {record.component_3_Fiber7.fibername}")

            if record.component_3_Fiber8 and record.component_3_Fiber8_Percentage:
                composition_info.append(f"{record.component_3_Fiber8_Percentage}% {record.component_3_Fiber8.fibername}")

            if record.component_3_Fiber9 and record.component_3_Fiber9_Percentage:
                composition_info.append(f"{record.component_3_Fiber9_Percentage}% {record.component_3_Fiber9.fibername}")

            if record.component_3_Fiber10 and record.component_3_Fiber10_Percentage:
                composition_info.append(f"{record.component_3_Fiber10_Percentage}% {record.component_3_Fiber10.fibername}")

            # Combine information for all fibers
            record.composition_3 = ', '.join(composition_info) if composition_info else False


    # component 4
    Component_4 = fields.Many2one('components_master', string='Select Component')
    Component_4_name = fields.Char(string='Selected Component', related='Component_4.ComponentName', readonly=True, store=True)

    component_4_Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1', store=True)
    component_4_fiber1_name = fields.Char(string='Fiber 1', related='component_4_Fiber1.fibername', readonly=True, store=True)
    component_4_Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    component_4_Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2', store=True)
    component_4_fiber2_name = fields.Char(string='Fiber 2', related='component_4_Fiber2.fibername', readonly=True, store=True)
    component_4_Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    component_4_Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3', store=True)
    component_4_fiber3_name = fields.Char(string='Fiber 3', related='component_4_Fiber3.fibername', readonly=True, store=True)
    component_4_Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    component_4_Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4', store=True)
    component_4_fiber4_name = fields.Char(string='Fiber 4', related='component_4_Fiber4.fibername', readonly=True, store=True)
    component_4_Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    component_4_Fiber5 = fields.Many2one('fiber_master', string='Select Fiber 5', store=True)
    component_4_fiber5_name = fields.Char(string='Fiber 5', related='component_4_Fiber5.fibername', readonly=True, store=True)
    component_4_Fiber5_Percentage = fields.Char(string='Fiber 5 Percentage', store=True)

    component_4_Fiber6 = fields.Many2one('fiber_master', string='Select Fiber 6', store=True)
    component_4_fiber6_name = fields.Char(string='Fiber 6', related='component_4_Fiber6.fibername', readonly=True, store=True)
    component_4_Fiber6_Percentage = fields.Char(string='Fiber 6 Percentage')

    component_4_Fiber7 = fields.Many2one('fiber_master', string='Select Fiber 7', store=True)
    component_4_fiber7_name = fields.Char(string='Fiber 7', related='component_4_Fiber7.fibername', readonly=True, store=True)
    component_4_Fiber7_Percentage = fields.Char(string='Fiber 7 Percentage', store=True)

    component_4_Fiber8 = fields.Many2one('fiber_master', string='Select Fiber 8', store=True)
    component_4_fiber8_name = fields.Char(string='Fiber 8', related='component_4_Fiber8.fibername', readonly=True, store=True)
    component_4_Fiber8_Percentage = fields.Char(string='Fiber 8 Percentage')

    component_4_Fiber9 = fields.Many2one('fiber_master', string='Select Fiber 9', store=True)
    component_4_fiber9_name = fields.Char(string='Fiber 9', related='component_4_Fiber9.fibername', readonly=True, store=True)
    component_4_Fiber9_Percentage = fields.Char(string='Fiber 9 Percentage')

    component_4_Fiber10 = fields.Many2one('fiber_master', string='Select Fiber 10', store=True)
    component_4_fiber10_name = fields.Char(string='Fiber 10', related='component_4_Fiber10.fibername', readonly=True, store=True)
    component_4_Fiber10_Percentage = fields.Char(string='Fiber 10 Percentage')


    composition_4 = fields.Char(string='Component 04', compute ='_fiber_create_4')


    @api.depends(
    'Component_4', 'component_4_Fiber1', 'component_4_Fiber1_Percentage',
    'component_4_Fiber2', 'component_4_Fiber2_Percentage',
    'component_4_Fiber3', 'component_4_Fiber3_Percentage',
    'component_4_Fiber4', 'component_4_Fiber4_Percentage',
    'component_4_Fiber5', 'component_4_Fiber5_Percentage',
    'component_4_Fiber6', 'component_4_Fiber6_Percentage',
    'component_4_Fiber7', 'component_4_Fiber7_Percentage',
    'component_4_Fiber8', 'component_4_Fiber8_Percentage',
    'component_4_Fiber9', 'component_4_Fiber9_Percentage',
    'component_4_Fiber10', 'component_4_Fiber10_Percentage'
    )

    def _fiber_create_4(self):
        for record in self:
            composition_info = []  # List to store information for each fiber

            if record.Component_4 and record.component_4_Fiber1 and record.component_4_Fiber1_Percentage:
                composition_info.append(f"{record.Component_4.ComponentName}: {record.component_4_Fiber1_Percentage}% {record.component_4_Fiber1.fibername}")

            if record.component_4_Fiber2 and record.component_4_Fiber2_Percentage:
                composition_info.append(f"{record.component_4_Fiber2_Percentage}% {record.component_4_Fiber2.fibername}")

            if record.component_4_Fiber3 and record.component_4_Fiber3_Percentage:
                composition_info.append(f"{record.component_4_Fiber3_Percentage}% {record.component_4_Fiber3.fibername}")

            if record.component_4_Fiber4 and record.component_4_Fiber4_Percentage:
                composition_info.append(f"{record.component_4_Fiber4_Percentage}% {record.component_4_Fiber4.fibername}")
                
            if record.component_4_Fiber5 and record.component_4_Fiber5_Percentage:
                composition_info.append(f"{record.component_4_Fiber5_Percentage}% {record.component_4_Fiber5.fibername}")

            if record.component_4_Fiber6 and record.component_4_Fiber6_Percentage:
                composition_info.append(f"{record.component_4_Fiber6_Percentage}% {record.component_4_Fiber6.fibername}")

            if record.component_4_Fiber7 and record.component_4_Fiber7_Percentage:
                composition_info.append(f"{record.component_4_Fiber7_Percentage}% {record.component_4_Fiber7.fibername}")

            if record.component_4_Fiber8 and record.component_4_Fiber8_Percentage:
                composition_info.append(f"{record.component_4_Fiber8_Percentage}% {record.component_4_Fiber8.fibername}")

            if record.component_4_Fiber9 and record.component_4_Fiber9_Percentage:
                composition_info.append(f"{record.component_4_Fiber9_Percentage}% {record.component_4_Fiber9.fibername}")

            if record.component_4_Fiber10 and record.component_4_Fiber10_Percentage:
                composition_info.append(f"{record.component_4_Fiber10_Percentage}% {record.component_4_Fiber10.fibername}")

            # Combine information for all fibers
            record.composition_4 = ', '.join(composition_info) if composition_info else False

    # component 5
    Component_5 = fields.Many2one('components_master', string='Select Component')
    Component_5_name = fields.Char(string='Selected Component', related='Component_5.ComponentName', readonly=True, store=True)

    component_5_Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1', store=True)
    component_5_fiber1_name = fields.Char(string='Fiber 1', related='component_5_Fiber1.fibername', readonly=True, store=True)
    component_5_Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    component_5_Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2', store=True)
    component_5_fiber2_name = fields.Char(string='Fiber 2', related='component_5_Fiber2.fibername', readonly=True, store=True)
    component_5_Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    component_5_Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3', store=True)
    component_5_fiber3_name = fields.Char(string='Fiber 3', related='component_5_Fiber3.fibername', readonly=True, store=True)
    component_5_Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    component_5_Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4', store=True)
    component_5_fiber4_name = fields.Char(string='Fiber 4', related='component_5_Fiber4.fibername', readonly=True, store=True)
    component_5_Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    component_5_Fiber5 = fields.Many2one('fiber_master', string='Select Fiber 5', store=True)
    component_5_fiber5_name = fields.Char(string='Fiber 5', related='component_5_Fiber5.fibername', readonly=True, store=True)
    component_5_Fiber5_Percentage = fields.Char(string='Fiber 5 Percentage', store=True)

    component_5_Fiber6 = fields.Many2one('fiber_master', string='Select Fiber 6', store=True)
    component_5_fiber6_name = fields.Char(string='Fiber 6', related='component_5_Fiber6.fibername', readonly=True, store=True)
    component_5_Fiber6_Percentage = fields.Char(string='Fiber 6 Percentage')

    component_5_Fiber7 = fields.Many2one('fiber_master', string='Select Fiber 7', store=True)
    component_5_fiber7_name = fields.Char(string='Fiber 7', related='component_5_Fiber7.fibername', readonly=True, store=True)
    component_5_Fiber7_Percentage = fields.Char(string='Fiber 7 Percentage', store=True)

    component_5_Fiber8 = fields.Many2one('fiber_master', string='Select Fiber 8', store=True)
    component_5_fiber8_name = fields.Char(string='Fiber 8', related='component_5_Fiber8.fibername', readonly=True, store=True)
    component_5_Fiber8_Percentage = fields.Char(string='Fiber 8 Percentage')

    component_5_Fiber9 = fields.Many2one('fiber_master', string='Select Fiber 9', store=True)
    component_5_fiber9_name = fields.Char(string='Fiber 9', related='component_5_Fiber9.fibername', readonly=True, store=True)
    component_5_Fiber9_Percentage = fields.Char(string='Fiber 9 Percentage')

    component_5_Fiber10 = fields.Many2one('fiber_master', string='Select Fiber 10', store=True)
    component_5_fiber10_name = fields.Char(string='Fiber 10', related='component_5_Fiber10.fibername', readonly=True, store=True)
    component_5_Fiber10_Percentage = fields.Char(string='Fiber 10 Percentage')


    composition_5 = fields.Char(string='Component 05', compute ='_fiber_create_5')



    @api.depends(
    'Component_5', 'component_5_Fiber1', 'component_5_Fiber1_Percentage',
    'component_5_Fiber2', 'component_5_Fiber2_Percentage',
    'component_5_Fiber3', 'component_5_Fiber3_Percentage',
    'component_5_Fiber4', 'component_5_Fiber4_Percentage',
    'component_5_Fiber5', 'component_5_Fiber5_Percentage',
    'component_5_Fiber6', 'component_5_Fiber6_Percentage',
    'component_5_Fiber7', 'component_5_Fiber7_Percentage',
    'component_5_Fiber8', 'component_5_Fiber8_Percentage',
    'component_5_Fiber9', 'component_5_Fiber9_Percentage',
    'component_5_Fiber10', 'component_5_Fiber10_Percentage'
    )

    def _fiber_create_5(self):
        for record in self:
            composition_info = []  # List to store information for each fiber

            if record.Component_5 and record.component_5_Fiber1 and record.component_5_Fiber1_Percentage:
                composition_info.append(f"{record.Component_5.ComponentName}: {record.component_5_Fiber1_Percentage}% {record.component_5_Fiber1.fibername}")

            if record.component_5_Fiber2 and record.component_5_Fiber2_Percentage:
                composition_info.append(f"{record.component_5_Fiber2_Percentage}% {record.component_5_Fiber2.fibername}")

            if record.component_5_Fiber3 and record.component_5_Fiber3_Percentage:
                composition_info.append(f"{record.component_5_Fiber3_Percentage}% {record.component_5_Fiber3.fibername}")

            if record.component_5_Fiber4 and record.component_5_Fiber4_Percentage:
                composition_info.append(f"{record.component_5_Fiber4_Percentage}% {record.component_5_Fiber4.fibername}")
                
            if record.component_5_Fiber5 and record.component_5_Fiber5_Percentage:
                composition_info.append(f"{record.component_5_Fiber5_Percentage}% {record.component_5_Fiber5.fibername}")

            if record.component_5_Fiber6 and record.component_5_Fiber6_Percentage:
                composition_info.append(f"{record.component_5_Fiber6_Percentage}% {record.component_5_Fiber6.fibername}")

            if record.component_5_Fiber7 and record.component_5_Fiber7_Percentage:
                composition_info.append(f"{record.component_5_Fiber7_Percentage}% {record.component_5_Fiber7.fibername}")

            if record.component_5_Fiber8 and record.component_5_Fiber8_Percentage:
                composition_info.append(f"{record.component_5_Fiber8_Percentage}% {record.component_5_Fiber8.fibername}")

            if record.component_5_Fiber9 and record.component_5_Fiber9_Percentage:
                composition_info.append(f"{record.component_5_Fiber9_Percentage}% {record.component_5_Fiber9.fibername}")

            if record.component_5_Fiber10 and record.component_5_Fiber10_Percentage:
                composition_info.append(f"{record.component_5_Fiber10_Percentage}% {record.component_5_Fiber10.fibername}")

            # Combine information for all fibers
            record.composition_5 = ', '.join(composition_info) if composition_info else False

    # component 6
    Component_6 = fields.Many2one('components_master', string='Select Component')
    Component_6_name = fields.Char(string='Selected Component', related='Component_6.ComponentName', readonly=True, store=True)

    component_6_Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1', store=True)
    component_6_fiber1_name = fields.Char(string='Fiber 1', related='component_6_Fiber1.fibername', readonly=True, store=True)
    component_6_Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    component_6_Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2', store=True)
    component_6_fiber2_name = fields.Char(string='Fiber 2', related='component_6_Fiber2.fibername', readonly=True, store=True)
    component_6_Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    component_6_Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3', store=True)
    component_6_fiber3_name = fields.Char(string='Fiber 3', related='component_6_Fiber3.fibername', readonly=True, store=True)
    component_6_Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    component_6_Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4', store=True)
    component_6_fiber4_name = fields.Char(string='Fiber 4', related='component_6_Fiber4.fibername', readonly=True, store=True)
    component_6_Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    component_6_Fiber5 = fields.Many2one('fiber_master', string='Select Fiber 5', store=True)
    component_6_fiber5_name = fields.Char(string='Fiber 5', related='component_6_Fiber5.fibername', readonly=True, store=True)
    component_6_Fiber5_Percentage = fields.Char(string='Fiber 5 Percentage', store=True)

    component_6_Fiber6 = fields.Many2one('fiber_master', string='Select Fiber 6', store=True)
    component_6_fiber6_name = fields.Char(string='Fiber 6', related='component_6_Fiber6.fibername', readonly=True, store=True)
    component_6_Fiber6_Percentage = fields.Char(string='Fiber 6 Percentage')

    component_6_Fiber7 = fields.Many2one('fiber_master', string='Select Fiber 7', store=True)
    component_6_fiber7_name = fields.Char(string='Fiber 7', related='component_6_Fiber7.fibername', readonly=True, store=True)
    component_6_Fiber7_Percentage = fields.Char(string='Fiber 7 Percentage', store=True)

    component_6_Fiber8 = fields.Many2one('fiber_master', string='Select Fiber 8', store=True)
    component_6_fiber8_name = fields.Char(string='Fiber 8', related='component_6_Fiber8.fibername', readonly=True, store=True)
    component_6_Fiber8_Percentage = fields.Char(string='Fiber 8 Percentage')

    component_6_Fiber9 = fields.Many2one('fiber_master', string='Select Fiber 9', store=True)
    component_6_fiber9_name = fields.Char(string='Fiber 9', related='component_6_Fiber9.fibername', readonly=True, store=True)
    component_6_Fiber9_Percentage = fields.Char(string='Fiber 9 Percentage')

    component_6_Fiber10 = fields.Many2one('fiber_master', string='Select Fiber 10', store=True)
    component_6_fiber10_name = fields.Char(string='Fiber 10', related='component_6_Fiber10.fibername', readonly=True, store=True)
    component_6_Fiber10_Percentage = fields.Char(string='Fiber 10 Percentage')

    composition_6 = fields.Char(string='Component 06', compute ='_fiber_create_6')

    @api.depends(
    'Component_6', 'component_6_Fiber1', 'component_6_Fiber1_Percentage',
    'component_6_Fiber2', 'component_6_Fiber2_Percentage',
    'component_6_Fiber3', 'component_6_Fiber3_Percentage',
    'component_6_Fiber4', 'component_6_Fiber4_Percentage',
    'component_6_Fiber5', 'component_6_Fiber5_Percentage',
    'component_6_Fiber6', 'component_6_Fiber6_Percentage',
    'component_6_Fiber7', 'component_6_Fiber7_Percentage',
    'component_6_Fiber8', 'component_6_Fiber8_Percentage',
    'component_6_Fiber9', 'component_6_Fiber9_Percentage',
    'component_6_Fiber10', 'component_6_Fiber10_Percentage'
    )

    def _fiber_create_6(self):
        for record in self:
            composition_info = []  # List to store information for each fiber

            if record.Component_6 and record.component_6_Fiber1 and record.component_6_Fiber1_Percentage:
                composition_info.append(f"{record.Component_6.ComponentName}: {record.component_6_Fiber1_Percentage}% {record.component_6_Fiber1.fibername}")

            if record.component_6_Fiber2 and record.component_6_Fiber2_Percentage:
                composition_info.append(f"{record.component_6_Fiber2_Percentage}% {record.component_6_Fiber2.fibername}")

            if record.component_6_Fiber3 and record.component_6_Fiber3_Percentage:
                composition_info.append(f"{record.component_6_Fiber3_Percentage}% {record.component_6_Fiber3.fibername}")

            if record.component_6_Fiber4 and record.component_6_Fiber4_Percentage:
                composition_info.append(f"{record.component_6_Fiber4_Percentage}% {record.component_6_Fiber4.fibername}")
                
            if record.component_6_Fiber5 and record.component_6_Fiber5_Percentage:
                composition_info.append(f"{record.component_6_Fiber5_Percentage}% {record.component_6_Fiber5.fibername}")

            if record.component_6_Fiber6 and record.component_6_Fiber6_Percentage:
                composition_info.append(f"{record.component_6_Fiber6_Percentage}% {record.component_6_Fiber6.fibername}")

            if record.component_6_Fiber7 and record.component_6_Fiber7_Percentage:
                composition_info.append(f"{record.component_6_Fiber7_Percentage}% {record.component_6_Fiber7.fibername}")

            if record.component_6_Fiber8 and record.component_6_Fiber8_Percentage:
                composition_info.append(f"{record.component_6_Fiber8_Percentage}% {record.component_6_Fiber8.fibername}")

            if record.component_6_Fiber9 and record.component_6_Fiber9_Percentage:
                composition_info.append(f"{record.component_6_Fiber9_Percentage}% {record.component_6_Fiber9.fibername}")

            if record.component_6_Fiber10 and record.component_6_Fiber10_Percentage:
                composition_info.append(f"{record.component_6_Fiber10_Percentage}% {record.component_6_Fiber10.fibername}")

            # Combine information for all fibers
            record.composition_6 = ', '.join(composition_info) if composition_info else False

    # component 7
    Component_7 = fields.Many2one('components_master', string='Select Component')
    Component_7_name = fields.Char(string='Selected Component', related='Component_7.ComponentName', readonly=True, store=True)

    component_7_Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1', store=True)
    component_7_fiber1_name = fields.Char(string='Fiber 1', related='component_7_Fiber1.fibername', readonly=True, store=True)
    component_7_Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    component_7_Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2', store=True)
    component_7_fiber2_name = fields.Char(string='Fiber 2', related='component_7_Fiber2.fibername', readonly=True, store=True)
    component_7_Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    component_7_Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3', store=True)
    component_7_fiber3_name = fields.Char(string='Fiber 3', related='component_7_Fiber3.fibername', readonly=True, store=True)
    component_7_Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    component_7_Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4', store=True)
    component_7_fiber4_name = fields.Char(string='Fiber 4', related='component_7_Fiber4.fibername', readonly=True, store=True)
    component_7_Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    component_7_Fiber5 = fields.Many2one('fiber_master', string='Select Fiber 5', store=True)
    component_7_fiber5_name = fields.Char(string='Fiber 5', related='component_7_Fiber5.fibername', readonly=True, store=True)
    component_7_Fiber5_Percentage = fields.Char(string='Fiber 5 Percentage', store=True)

    component_7_Fiber6 = fields.Many2one('fiber_master', string='Select Fiber 6', store=True)
    component_7_fiber6_name = fields.Char(string='Fiber 6', related='component_7_Fiber6.fibername', readonly=True, store=True)
    component_7_Fiber6_Percentage = fields.Char(string='Fiber 6 Percentage')

    component_7_Fiber7 = fields.Many2one('fiber_master', string='Select Fiber 7', store=True)
    component_7_fiber7_name = fields.Char(string='Fiber 7', related='component_7_Fiber7.fibername', readonly=True, store=True)
    component_7_Fiber7_Percentage = fields.Char(string='Fiber 7 Percentage', store=True)

    component_7_Fiber8 = fields.Many2one('fiber_master', string='Select Fiber 8', store=True)
    component_7_fiber8_name = fields.Char(string='Fiber 8', related='component_7_Fiber8.fibername', readonly=True, store=True)
    component_7_Fiber8_Percentage = fields.Char(string='Fiber 8 Percentage')

    component_7_Fiber9 = fields.Many2one('fiber_master', string='Select Fiber 9', store=True)
    component_7_fiber9_name = fields.Char(string='Fiber 9', related='component_7_Fiber9.fibername', readonly=True, store=True)
    component_7_Fiber9_Percentage = fields.Char(string='Fiber 9 Percentage')

    component_7_Fiber10 = fields.Many2one('fiber_master', string='Select Fiber 10', store=True)
    component_7_fiber10_name = fields.Char(string='Fiber 10', related='component_7_Fiber10.fibername', readonly=True, store=True)
    component_7_Fiber10_Percentage = fields.Char(string='Fiber 10 Percentage')

    composition_7 = fields.Char(string='Component 07', compute ='_fiber_create_7')

    @api.depends(
    'Component_7', 'component_7_Fiber1', 'component_7_Fiber1_Percentage',
    'component_7_Fiber2', 'component_7_Fiber2_Percentage',
    'component_7_Fiber3', 'component_7_Fiber3_Percentage',
    'component_7_Fiber4', 'component_7_Fiber4_Percentage',
    'component_7_Fiber5', 'component_7_Fiber5_Percentage',
    'component_7_Fiber6', 'component_7_Fiber6_Percentage',
    'component_7_Fiber7', 'component_7_Fiber7_Percentage',
    'component_7_Fiber8', 'component_7_Fiber8_Percentage',
    'component_7_Fiber9', 'component_7_Fiber9_Percentage',
    'component_7_Fiber10', 'component_7_Fiber10_Percentage'
    )

    def _fiber_create_7(self):
        for record in self:
            composition_info = []  # List to store information for each fiber

            if record.Component_7 and record.component_7_Fiber1 and record.component_7_Fiber1_Percentage:
                composition_info.append(f"{record.Component_7.ComponentName}: {record.component_7_Fiber1_Percentage}% {record.component_7_Fiber1.fibername}")

            if record.component_7_Fiber2 and record.component_7_Fiber2_Percentage:
                composition_info.append(f"{record.component_7_Fiber2_Percentage}% {record.component_7_Fiber2.fibername}")

            if record.component_7_Fiber3 and record.component_7_Fiber3_Percentage:
                composition_info.append(f"{record.component_7_Fiber3_Percentage}% {record.component_7_Fiber3.fibername}")

            if record.component_7_Fiber4 and record.component_7_Fiber4_Percentage:
                composition_info.append(f"{record.component_7_Fiber4_Percentage}% {record.component_7_Fiber4.fibername}")
                
            if record.component_7_Fiber5 and record.component_7_Fiber5_Percentage:
                composition_info.append(f"{record.component_7_Fiber5_Percentage}% {record.component_7_Fiber5.fibername}")

            if record.component_7_Fiber6 and record.component_7_Fiber6_Percentage:
                composition_info.append(f"{record.component_7_Fiber6_Percentage}% {record.component_7_Fiber6.fibername}")

            if record.component_7_Fiber7 and record.component_7_Fiber7_Percentage:
                composition_info.append(f"{record.component_7_Fiber7_Percentage}% {record.component_7_Fiber7.fibername}")

            if record.component_7_Fiber8 and record.component_7_Fiber8_Percentage:
                composition_info.append(f"{record.component_7_Fiber8_Percentage}% {record.component_7_Fiber8.fibername}")

            if record.component_7_Fiber9 and record.component_7_Fiber9_Percentage:
                composition_info.append(f"{record.component_7_Fiber9_Percentage}% {record.component_7_Fiber9.fibername}")

            if record.component_7_Fiber10 and record.component_7_Fiber10_Percentage:
                composition_info.append(f"{record.component_7_Fiber10_Percentage}% {record.component_7_Fiber10.fibername}")

            # Combine information for all fibers
            record.composition_7 = ', '.join(composition_info) if composition_info else False

    # component 8
    Component_8 = fields.Many2one('components_master', string='Select Component')
    Component_8_name = fields.Char(string='Selected Component', related='Component_8.ComponentName', readonly=True, store=True)

    component_8_Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1', store=True)
    component_8_fiber1_name = fields.Char(string='Fiber 1', related='component_8_Fiber1.fibername', readonly=True, store=True)
    component_8_Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    component_8_Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2', store=True)
    component_8_fiber2_name = fields.Char(string='Fiber 2', related='component_8_Fiber2.fibername', readonly=True, store=True)
    component_8_Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    component_8_Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3', store=True)
    component_8_fiber3_name = fields.Char(string='Fiber 3', related='component_8_Fiber3.fibername', readonly=True, store=True)
    component_8_Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    component_8_Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4', store=True)
    component_8_fiber4_name = fields.Char(string='Fiber 4', related='component_8_Fiber4.fibername', readonly=True, store=True)
    component_8_Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    component_8_Fiber5 = fields.Many2one('fiber_master', string='Select Fiber 5', store=True)
    component_8_fiber5_name = fields.Char(string='Fiber 5', related='component_8_Fiber5.fibername', readonly=True, store=True)
    component_8_Fiber5_Percentage = fields.Char(string='Fiber 5 Percentage', store=True)

    component_8_Fiber6 = fields.Many2one('fiber_master', string='Select Fiber 6', store=True)
    component_8_fiber6_name = fields.Char(string='Fiber 6', related='component_8_Fiber6.fibername', readonly=True, store=True)
    component_8_Fiber6_Percentage = fields.Char(string='Fiber 6 Percentage')

    component_8_Fiber7 = fields.Many2one('fiber_master', string='Select Fiber 7', store=True)
    component_8_fiber7_name = fields.Char(string='Fiber 7', related='component_8_Fiber7.fibername', readonly=True, store=True)
    component_8_Fiber7_Percentage = fields.Char(string='Fiber 7 Percentage', store=True)

    component_8_Fiber8 = fields.Many2one('fiber_master', string='Select Fiber 8', store=True)
    component_8_fiber8_name = fields.Char(string='Fiber 8', related='component_8_Fiber8.fibername', readonly=True, store=True)
    component_8_Fiber8_Percentage = fields.Char(string='Fiber 8 Percentage')

    component_8_Fiber9 = fields.Many2one('fiber_master', string='Select Fiber 9', store=True)
    component_8_fiber9_name = fields.Char(string='Fiber 9', related='component_8_Fiber9.fibername', readonly=True, store=True)
    component_8_Fiber9_Percentage = fields.Char(string='Fiber 9 Percentage')

    component_8_Fiber10 = fields.Many2one('fiber_master', string='Select Fiber 10', store=True)
    component_8_fiber10_name = fields.Char(string='Fiber 10', related='component_8_Fiber10.fibername', readonly=True, store=True)
    component_8_Fiber10_Percentage = fields.Char(string='Fiber 10 Percentage')

    composition_8 = fields.Char(string='Component 08', compute ='_fiber_create_8')

    @api.depends(
        'Component_8', 'component_8_Fiber1', 'component_8_Fiber1_Percentage',
        'component_8_Fiber2', 'component_8_Fiber2_Percentage',
        'component_8_Fiber3', 'component_8_Fiber3_Percentage',
        'component_8_Fiber4', 'component_8_Fiber4_Percentage',
        'component_8_Fiber5', 'component_8_Fiber5_Percentage',
        'component_8_Fiber6', 'component_8_Fiber6_Percentage',
        'component_8_Fiber7', 'component_8_Fiber7_Percentage',
        'component_8_Fiber8', 'component_8_Fiber8_Percentage',
        'component_8_Fiber9', 'component_8_Fiber9_Percentage',
        'component_8_Fiber10', 'component_8_Fiber10_Percentage'
        )

    def _fiber_create_8(self):
        for record in self:
            composition_info = []  # List to store information for each fiber

            if record.Component_8 and record.component_8_Fiber1 and record.component_8_Fiber1_Percentage:
                composition_info.append(f"{record.Component_8.ComponentName}: {record.component_8_Fiber1_Percentage}% {record.component_8_Fiber1.fibername}")

            if record.component_8_Fiber2 and record.component_8_Fiber2_Percentage:
                composition_info.append(f"{record.component_8_Fiber2_Percentage}% {record.component_8_Fiber2.fibername}")

            if record.component_8_Fiber3 and record.component_8_Fiber3_Percentage:
                composition_info.append(f"{record.component_8_Fiber3_Percentage}% {record.component_8_Fiber3.fibername}")

            if record.component_8_Fiber4 and record.component_8_Fiber4_Percentage:
                composition_info.append(f"{record.component_8_Fiber4_Percentage}% {record.component_8_Fiber4.fibername}")
                
            if record.component_8_Fiber5 and record.component_8_Fiber5_Percentage:
                composition_info.append(f"{record.component_8_Fiber5_Percentage}% {record.component_8_Fiber5.fibername}")

            if record.component_8_Fiber6 and record.component_8_Fiber6_Percentage:
                composition_info.append(f"{record.component_8_Fiber6_Percentage}% {record.component_8_Fiber6.fibername}")

            if record.component_8_Fiber7 and record.component_8_Fiber7_Percentage:
                composition_info.append(f"{record.component_8_Fiber7_Percentage}% {record.component_8_Fiber7.fibername}")

            if record.component_8_Fiber8 and record.component_8_Fiber8_Percentage:
                composition_info.append(f"{record.component_8_Fiber8_Percentage}% {record.component_8_Fiber8.fibername}")

            if record.component_8_Fiber9 and record.component_8_Fiber9_Percentage:
                composition_info.append(f"{record.component_8_Fiber9_Percentage}% {record.component_8_Fiber9.fibername}")

            if record.component_8_Fiber10 and record.component_8_Fiber10_Percentage:
                composition_info.append(f"{record.component_8_Fiber10_Percentage}% {record.component_8_Fiber10.fibername}")

            # Combine information for all fibers
            record.composition_8 = ', '.join(composition_info) if composition_info else False
    
    # component 9
    Component_9 = fields.Many2one('components_master', string='Select Component')
    Component_9_name = fields.Char(string='Selected Component', related='Component_9.ComponentName', readonly=True, store=True)

    component_9_Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1', store=True)
    component_9_fiber1_name = fields.Char(string='Fiber 1', related='component_9_Fiber1.fibername', readonly=True, store=True)
    component_9_Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    component_9_Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2', store=True)
    component_9_fiber2_name = fields.Char(string='Fiber 2', related='component_9_Fiber2.fibername', readonly=True, store=True)
    component_9_Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    component_9_Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3', store=True)
    component_9_fiber3_name = fields.Char(string='Fiber 3', related='component_9_Fiber3.fibername', readonly=True, store=True)
    component_9_Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    component_9_Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4', store=True)
    component_9_fiber4_name = fields.Char(string='Fiber 4', related='component_9_Fiber4.fibername', readonly=True, store=True)
    component_9_Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    component_9_Fiber5 = fields.Many2one('fiber_master', string='Select Fiber 5', store=True)
    component_9_fiber5_name = fields.Char(string='Fiber 5', related='component_9_Fiber5.fibername', readonly=True, store=True)
    component_9_Fiber5_Percentage = fields.Char(string='Fiber 5 Percentage', store=True)

    component_9_Fiber6 = fields.Many2one('fiber_master', string='Select Fiber 6', store=True)
    component_9_fiber6_name = fields.Char(string='Fiber 6', related='component_9_Fiber6.fibername', readonly=True, store=True)
    component_9_Fiber6_Percentage = fields.Char(string='Fiber 6 Percentage')

    component_9_Fiber7 = fields.Many2one('fiber_master', string='Select Fiber 7', store=True)
    component_9_fiber7_name = fields.Char(string='Fiber 7', related='component_9_Fiber7.fibername', readonly=True, store=True)
    component_9_Fiber7_Percentage = fields.Char(string='Fiber 7 Percentage', store=True)

    component_9_Fiber8 = fields.Many2one('fiber_master', string='Select Fiber 8', store=True)
    component_9_fiber8_name = fields.Char(string='Fiber 8', related='component_9_Fiber8.fibername', readonly=True, store=True)
    component_9_Fiber8_Percentage = fields.Char(string='Fiber 8 Percentage')

    component_9_Fiber9 = fields.Many2one('fiber_master', string='Select Fiber 9', store=True)
    component_9_fiber9_name = fields.Char(string='Fiber 9', related='component_9_Fiber9.fibername', readonly=True, store=True)
    component_9_Fiber9_Percentage = fields.Char(string='Fiber 9 Percentage')

    component_9_Fiber10 = fields.Many2one('fiber_master', string='Select Fiber 10', store=True)
    component_9_fiber10_name = fields.Char(string='Fiber 10', related='component_9_Fiber10.fibername', readonly=True, store=True)
    component_9_Fiber10_Percentage = fields.Char(string='Fiber 10 Percentage')

    composition_9 = fields.Char(string='Component 09' , compute ='_fiber_create_9')

    @api.depends(
        'Component_9', 'component_9_Fiber1', 'component_9_Fiber1_Percentage',
        'component_9_Fiber2', 'component_9_Fiber2_Percentage',
        'component_9_Fiber3', 'component_9_Fiber3_Percentage',
        'component_9_Fiber4', 'component_9_Fiber4_Percentage',
        'component_9_Fiber5', 'component_9_Fiber5_Percentage',
        'component_9_Fiber6', 'component_9_Fiber6_Percentage',
        'component_9_Fiber7', 'component_9_Fiber7_Percentage',
        'component_9_Fiber8', 'component_9_Fiber8_Percentage',
        'component_9_Fiber9', 'component_9_Fiber9_Percentage',
        'component_9_Fiber10', 'component_9_Fiber10_Percentage'
        )

    def _fiber_create_9(self):
        for record in self:
            composition_info = []  # List to store information for each fiber

            if record.Component_9 and record.component_9_Fiber1 and record.component_9_Fiber1_Percentage:
                composition_info.append(f"{record.Component_9.ComponentName}: {record.component_9_Fiber1_Percentage}% {record.component_9_Fiber1.fibername}")

            if record.component_9_Fiber2 and record.component_9_Fiber2_Percentage:
                composition_info.append(f"{record.component_9_Fiber2_Percentage}% {record.component_9_Fiber2.fibername}")

            if record.component_9_Fiber3 and record.component_9_Fiber3_Percentage:
                composition_info.append(f"{record.component_9_Fiber3_Percentage}% {record.component_9_Fiber3.fibername}")

            if record.component_9_Fiber4 and record.component_9_Fiber4_Percentage:
                composition_info.append(f"{record.component_9_Fiber4_Percentage}% {record.component_9_Fiber4.fibername}")
                
            if record.component_9_Fiber5 and record.component_9_Fiber5_Percentage:
                composition_info.append(f"{record.component_9_Fiber5_Percentage}% {record.component_9_Fiber5.fibername}")

            if record.component_9_Fiber6 and record.component_9_Fiber6_Percentage:
                composition_info.append(f"{record.component_9_Fiber6_Percentage}% {record.component_9_Fiber6.fibername}")

            if record.component_9_Fiber7 and record.component_9_Fiber7_Percentage:
                composition_info.append(f"{record.component_9_Fiber7_Percentage}% {record.component_9_Fiber7.fibername}")

            if record.component_9_Fiber8 and record.component_9_Fiber8_Percentage:
                composition_info.append(f"{record.component_9_Fiber8_Percentage}% {record.component_9_Fiber8.fibername}")

            if record.component_9_Fiber9 and record.component_9_Fiber9_Percentage:
                composition_info.append(f"{record.component_9_Fiber9_Percentage}% {record.component_9_Fiber9.fibername}")

            if record.component_9_Fiber10 and record.component_9_Fiber10_Percentage:
                composition_info.append(f"{record.component_9_Fiber10_Percentage}% {record.component_9_Fiber10.fibername}")

            # Combine information for all fibers
            record.composition_9 = ', '.join(composition_info) if composition_info else False

    # component 10
    Component_10 = fields.Many2one('components_master', string='Select Component', store=True)
    Component_10_name = fields.Char(string='Selected Component', related='Component_10.ComponentName', readonly=True, store=True)

    component_10_Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1', store=True)
    component_10_fiber1_name = fields.Char(string='Fiber 1', related='component_10_Fiber1.fibername', readonly=True, store=True)
    component_10_Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    component_10_Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2', store=True)
    component_10_fiber2_name = fields.Char(string='Fiber 2', related='component_10_Fiber2.fibername', readonly=True, store=True)
    component_10_Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    component_10_Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3', store=True)
    component_10_fiber3_name = fields.Char(string='Fiber 3', related='component_10_Fiber3.fibername', readonly=True, store=True)
    component_10_Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    component_10_Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4', store=True)
    component_10_fiber4_name = fields.Char(string='Fiber 4', related='component_10_Fiber4.fibername', readonly=True, store=True)
    component_10_Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    component_10_Fiber5 = fields.Many2one('fiber_master', string='Select Fiber 5', store=True)
    component_10_fiber5_name = fields.Char(string='Fiber 5', related='component_10_Fiber5.fibername', readonly=True, store=True)
    component_10_Fiber5_Percentage = fields.Char(string='Fiber 5 Percentage', store=True)

    component_10_Fiber6 = fields.Many2one('fiber_master', string='Select Fiber 6', store=True)
    component_10_fiber6_name = fields.Char(string='Fiber 6', related='component_10_Fiber6.fibername', readonly=True, store=True)
    component_10_Fiber6_Percentage = fields.Char(string='Fiber 6 Percentage')

    component_10_Fiber7 = fields.Many2one('fiber_master', string='Select Fiber 7', store=True)
    component_10_fiber7_name = fields.Char(string='Fiber 7', related='component_10_Fiber7.fibername', readonly=True, store=True)
    component_10_Fiber7_Percentage = fields.Char(string='Fiber 7 Percentage', store=True)

    component_10_Fiber8 = fields.Many2one('fiber_master', string='Select Fiber 8', store=True)
    component_10_fiber8_name = fields.Char(string='Fiber 8', related='component_10_Fiber8.fibername', readonly=True, store=True)
    component_10_Fiber8_Percentage = fields.Char(string='Fiber 8 Percentage')

    component_10_Fiber9 = fields.Many2one('fiber_master', string='Select Fiber 9', store=True)
    component_10_fiber9_name = fields.Char(string='Fiber 9', related='component_10_Fiber9.fibername', readonly=True, store=True)
    component_10_Fiber9_Percentage = fields.Char(string='Fiber 9 Percentage')

    component_10_Fiber10 = fields.Many2one('fiber_master', string='Select Fiber 10', store=True)
    component_10_fiber10_name = fields.Char(string='Fiber 10', related='component_10_Fiber10.fibername', readonly=True, store=True)
    component_10_Fiber10_Percentage = fields.Char(string='Fiber 10 Percentage')

    composition_10 = fields.Char(string='Component 10', compute ='_fiber_create_10')

    @api.depends(
        'Component_10', 'component_10_Fiber1', 'component_10_Fiber1_Percentage',
        'component_10_Fiber2', 'component_10_Fiber2_Percentage',
        'component_10_Fiber3', 'component_10_Fiber3_Percentage',
        'component_10_Fiber4', 'component_10_Fiber4_Percentage',
        'component_10_Fiber5', 'component_10_Fiber5_Percentage',
        'component_10_Fiber6', 'component_10_Fiber6_Percentage',
        'component_10_Fiber7', 'component_10_Fiber7_Percentage',
        'component_10_Fiber8', 'component_10_Fiber8_Percentage',
        'component_10_Fiber9', 'component_10_Fiber9_Percentage',
        'component_10_Fiber10', 'component_10_Fiber10_Percentage'
        )

    def _fiber_create_10(self):
        for record in self:
            composition_info = []  # List to store information for each fiber

            if record.Component_10 and record.component_10_Fiber1 and record.component_10_Fiber1_Percentage:
                composition_info.append(f"{record.Component_10.ComponentName}: {record.component_10_Fiber1_Percentage}% {record.component_10_Fiber1.fibername}")

            if record.component_10_Fiber2 and record.component_10_Fiber2_Percentage:
                composition_info.append(f"{record.component_10_Fiber2_Percentage}% {record.component_10_Fiber2.fibername}")

            if record.component_10_Fiber3 and record.component_10_Fiber3_Percentage:
                composition_info.append(f"{record.component_10_Fiber3_Percentage}% {record.component_10_Fiber3.fibername}")

            if record.component_10_Fiber4 and record.component_10_Fiber4_Percentage:
                composition_info.append(f"{record.component_10_Fiber4_Percentage}% {record.component_10_Fiber4.fibername}")
                
            if record.component_10_Fiber5 and record.component_10_Fiber5_Percentage:
                composition_info.append(f"{record.component_10_Fiber5_Percentage}% {record.component_10_Fiber5.fibername}")

            if record.component_10_Fiber6 and record.component_10_Fiber6_Percentage:
                composition_info.append(f"{record.component_10_Fiber6_Percentage}% {record.component_10_Fiber6.fibername}")

            if record.component_10_Fiber7 and record.component_10_Fiber7_Percentage:
                composition_info.append(f"{record.component_10_Fiber7_Percentage}% {record.component_10_Fiber7.fibername}")

            if record.component_10_Fiber8 and record.component_10_Fiber8_Percentage:
                composition_info.append(f"{record.component_10_Fiber8_Percentage}% {record.component_10_Fiber8.fibername}")

            if record.component_10_Fiber9 and record.component_10_Fiber9_Percentage:
                composition_info.append(f"{record.component_10_Fiber9_Percentage}% {record.component_10_Fiber9.fibername}")

            if record.component_10_Fiber10 and record.component_10_Fiber10_Percentage:
                composition_info.append(f"{record.component_10_Fiber10_Percentage}% {record.component_10_Fiber10.fibername}")

            # Combine information for all fibers
            record.composition_10 = ', '.join(composition_info) if composition_info else False


    discription = fields.Char(string='combine')
    discription01 = fields.Char(string='COMPOSITION 01', related="composition_lines.discription")

    # 2023-12-18
    id = fields.Integer(string = 'Id')


class Clines(models.Model):
    _name = "composition_lines"
    _description = "composition lines"
    _rec_name = 'Component'

    connect = fields.Many2one('composition_master', string="connect")
    Component = fields.Many2one('components_master', string="Component")

    Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1')
    Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2')
    Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3')
    Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4')
    Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    discription = fields.Char(string='Composition' , compute = '_compute_so_ref_lv')

    @api.depends('Component', 'Fiber1','Fiber1_Percentage','Fiber2','Fiber2_Percentage')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both SoNumber and SoOrderItem have values
            if record.Component and record.Fiber1 and record.Fiber1_Percentage and record.Fiber2 and record.Fiber2_Percentage:
                record.discription = f"{record.Component.ComponentName}: {record.Fiber1_Percentage}% {record.Fiber1.fibername}, {record.Fiber2_Percentage}% {record.Fiber2.fibername}"
            else:
                record.discription = False


class ClinesTab2(models.Model):
    _name = "composition_lines_tab_02"
    _description = "composition lines"
    _rec_name = 'discription'

    connect01 = fields.Many2one('composition_master', string="connect")
    Component = fields.Many2one('components_master', string="Component")
    
    

    Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1')
    Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2')
    Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    # Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3')
    # Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    # Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4')
    # Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    discription = fields.Char(string='Composition' , compute = '_compute_so_ref_lv')

    @api.depends('Component', 'Fiber1','Fiber1_Percentage','Fiber2','Fiber2_Percentage')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both SoNumber and SoOrderItem have values
            if record.Component and record.Fiber1 and record.Fiber1_Percentage and record.Fiber2 and record.Fiber2_Percentage:
                record.discription = f"{record.Component.ComponentName}: {record.Fiber1_Percentage}% {record.Fiber1.fibername}, {record.Fiber2_Percentage}% {record.Fiber2.fibername}"
            else:
                record.discription = False


class ClinesTab3(models.Model):
    _name = "composition_lines_tab_03"
    _description = "composition lines"
    _rec_name = 'discription'

    connect03 = fields.Many2one('composition_master', string="connect")
    Component = fields.Many2one('components_master', string="Component")
    
    

    Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1')
    Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2')
    Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    # Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3')
    # Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    # Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4')
    # Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    discription = fields.Char(string='Composition' , compute = '_compute_so_ref_lv')

    @api.depends('Component', 'Fiber1','Fiber1_Percentage','Fiber2','Fiber2_Percentage')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both SoNumber and SoOrderItem have values
            if record.Component and record.Fiber1 and record.Fiber1_Percentage and record.Fiber2 and record.Fiber2_Percentage:
                record.discription = f"{record.Component.ComponentName}: {record.Fiber1_Percentage}% {record.Fiber1.fibername}, {record.Fiber2_Percentage}% {record.Fiber2.fibername}"
            else:
                record.discription = False


class ClinesTab4(models.Model):
    _name = "composition_lines_tab_04"
    _description = "composition lines"
    _rec_name = 'discription'

    connect04 = fields.Many2one('composition_master', string="connect")
    Component = fields.Many2one('components_master', string="Component")
    
    

    Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1')
    Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2')
    Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    # Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3')
    # Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    # Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4')
    # Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    discription = fields.Char(string='Composition' , compute = '_compute_so_ref_lv')

    @api.depends('Component', 'Fiber1','Fiber1_Percentage','Fiber2','Fiber2_Percentage')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both SoNumber and SoOrderItem have values
            if record.Component and record.Fiber1 and record.Fiber1_Percentage and record.Fiber2 and record.Fiber2_Percentage:
                record.discription = f"{record.Component.ComponentName}: {record.Fiber1_Percentage}% {record.Fiber1.fibername}, {record.Fiber2_Percentage}% {record.Fiber2.fibername}"
            else:
                record.discription = False



class ClinesTab5(models.Model):
    _name = "composition_lines_tab_05"
    _description = "composition lines"
    _rec_name = 'discription'

    connect05 = fields.Many2one('composition_master', string="connect")
    Component = fields.Many2one('components_master', string="Component")
    
    

    Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1')
    Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2')
    Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    # Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3')
    # Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    # Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4')
    # Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    discription = fields.Char(string='Composition' , compute = '_compute_so_ref_lv')

    @api.depends('Component', 'Fiber1','Fiber1_Percentage','Fiber2','Fiber2_Percentage')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both SoNumber and SoOrderItem have values
            if record.Component and record.Fiber1 and record.Fiber1_Percentage and record.Fiber2 and record.Fiber2_Percentage:
                record.discription = f"{record.Component.ComponentName}: {record.Fiber1_Percentage}% {record.Fiber1.fibername}, {record.Fiber2_Percentage}% {record.Fiber2.fibername}"
            else:
                record.discription = False



class ClinesTab6(models.Model):
    _name = "composition_lines_tab_06"
    _description = "composition lines"
    _rec_name = 'discription'

    connect06 = fields.Many2one('composition_master', string="connect")
    Component = fields.Many2one('components_master', string="Component")
    
    

    Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1')
    Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2')
    Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    # Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3')
    # Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    # Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4')
    # Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    discription = fields.Char(string='Composition' , compute = '_compute_so_ref_lv')

    @api.depends('Component', 'Fiber1','Fiber1_Percentage','Fiber2','Fiber2_Percentage')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both SoNumber and SoOrderItem have values
            if record.Component and record.Fiber1 and record.Fiber1_Percentage and record.Fiber2 and record.Fiber2_Percentage:
                record.discription = f"{record.Component.ComponentName}: {record.Fiber1_Percentage}% {record.Fiber1.fibername}, {record.Fiber2_Percentage}% {record.Fiber2.fibername}"
            else:
                record.discription = False



class ClinesTab7(models.Model):
    _name = "composition_lines_tab_07"
    _description = "composition lines"
    _rec_name = 'discription'

    connect07 = fields.Many2one('composition_master', string="connect")
    Component = fields.Many2one('components_master', string="Component")
    
    

    Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1')
    Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2')
    Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    # Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3')
    # Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    # Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4')
    # Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    discription = fields.Char(string='Composition' , compute = '_compute_so_ref_lv')

    @api.depends('Component', 'Fiber1','Fiber1_Percentage','Fiber2','Fiber2_Percentage')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both SoNumber and SoOrderItem have values
            if record.Component and record.Fiber1 and record.Fiber1_Percentage and record.Fiber2 and record.Fiber2_Percentage:
                record.discription = f"{record.Component.ComponentName}: {record.Fiber1_Percentage}% {record.Fiber1.fibername}, {record.Fiber2_Percentage}% {record.Fiber2.fibername}"
            else:
                record.discription = False


class ClinesTab8(models.Model):
    _name = "composition_lines_tab_08"
    _description = "composition lines"
    _rec_name = 'discription'

    connect08 = fields.Many2one('composition_master', string="connect")
    Component = fields.Many2one('components_master', string="Component")
    
    

    Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1')
    Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2')
    Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    # Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3')
    # Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    # Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4')
    # Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    discription = fields.Char(string='Composition' , compute = '_compute_so_ref_lv')

    @api.depends('Component', 'Fiber1','Fiber1_Percentage','Fiber2','Fiber2_Percentage')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both SoNumber and SoOrderItem have values
            if record.Component and record.Fiber1 and record.Fiber1_Percentage and record.Fiber2 and record.Fiber2_Percentage:
                record.discription = f"{record.Component.ComponentName}: {record.Fiber1_Percentage}% {record.Fiber1.fibername}, {record.Fiber2_Percentage}% {record.Fiber2.fibername}"
            else:
                record.discription = False



class ClinesTab9(models.Model):
    _name = "composition_lines_tab_09"
    _description = "composition lines"
    _rec_name = 'discription'

    connect09 = fields.Many2one('composition_master', string="connect")
    Component = fields.Many2one('components_master', string="Component")
    
    

    Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1')
    Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2')
    Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    # Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3')
    # Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    # Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4')
    # Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    discription = fields.Char(string='Composition' , compute = '_compute_so_ref_lv')

    @api.depends('Component', 'Fiber1','Fiber1_Percentage','Fiber2','Fiber2_Percentage')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both SoNumber and SoOrderItem have values
            if record.Component and record.Fiber1 and record.Fiber1_Percentage and record.Fiber2 and record.Fiber2_Percentage:
                record.discription = f"{record.Component.ComponentName}: {record.Fiber1_Percentage}% {record.Fiber1.fibername}, {record.Fiber2_Percentage}% {record.Fiber2.fibername}"
            else:
                record.discription = False


class ClinesTab10(models.Model):
    _name = "composition_lines_tab_010"
    _description = "composition lines"
    _rec_name = 'discription'

    connect010 = fields.Many2one('composition_master', string="connect")
    Component = fields.Many2one('components_master', string="Component")
    
    

    Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1')
    Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2')
    Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    # Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3')
    # Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    # Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4')
    # Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    discription = fields.Char(string='Composition' , compute = '_compute_so_ref_lv')

    @api.depends('Component', 'Fiber1','Fiber1_Percentage','Fiber2','Fiber2_Percentage')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both SoNumber and SoOrderItem have values
            if record.Component and record.Fiber1 and record.Fiber1_Percentage and record.Fiber2 and record.Fiber2_Percentage:
                record.discription = f"{record.Component.ComponentName}: {record.Fiber1_Percentage}% {record.Fiber1.fibername}, {record.Fiber2_Percentage}% {record.Fiber2.fibername}"
            else:
                record.discription = False



class ClinesTab11(models.Model):
    _name = "composition_lines_tab_011"
    _description = "composition lines"
    _rec_name = 'discription'

    connect011 = fields.Many2one('composition_master', string="connect")
    Component = fields.Many2one('components_master', string="Component")
    
    

    Fiber1 = fields.Many2one('fiber_master', string='Select Fiber 1')
    Fiber1_Percentage = fields.Char(string='Fiber 1 Percentage')

    Fiber2 = fields.Many2one('fiber_master', string='Select Fiber 2')
    Fiber2_Percentage = fields.Char(string='Fiber 2 Percentage')

    # Fiber3 = fields.Many2one('fiber_master', string='Select Fiber 3')
    # Fiber3_Percentage = fields.Char(string='Fiber 3 Percentage')

    # Fiber4 = fields.Many2one('fiber_master', string='Select Fiber 4')
    # Fiber4_Percentage = fields.Char(string='Fiber 4 Percentage')

    discription = fields.Char(string='Composition' , compute = '_compute_so_ref_lv')

    @api.depends('Component', 'Fiber1','Fiber1_Percentage','Fiber2','Fiber2_Percentage')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both SoNumber and SoOrderItem have values
            if record.Component and record.Fiber1 and record.Fiber1_Percentage and record.Fiber2 and record.Fiber2_Percentage:
                record.discription = f"{record.Component.ComponentName}: {record.Fiber1_Percentage}% {record.Fiber1.fibername}, {record.Fiber2_Percentage}% {record.Fiber2.fibername}"
            else:
                record.discription = False






    
