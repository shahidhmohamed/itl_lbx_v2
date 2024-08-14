from odoo import models, fields,api, _

class GetPoLines(models.Model):
    _name = 'get_po_mas_lines'
    _description = 'Purchase Order Lines'

    header_table = fields.Many2one('get_po_mas', string='Purchase Order Reference', ondelete='cascade')
    
    # Fields from PurchaseOrder
    po_number = fields.Char(string='PO Number')
    purchase_order_version = fields.Char(string='PO Version')
    po_date = fields.Date(string='PO Date')
    last_revision_date = fields.Date(string='Last Revision Date')
    currency = fields.Char(string='Currency')
    consignee_name = fields.Char(string='Consignee Name')
    consignee_name2 = fields.Char(string='Consignee Name 2')
    consignee_name3 = fields.Char(string='Consignee Name 3')
    consignee_add1 = fields.Char(string='Consignee Address 1')
    consignee_add2 = fields.Char(string='Consignee Address 2')
    contact_person = fields.Char(string='Contact Person')
    contact_tel = fields.Char(string='Contact Tel')
    contact_email = fields.Char(string='Contact Email')
    supplier_name = fields.Char(string='Supplier Name')
    supplier_add1 = fields.Char(string='Supplier Address 1')
    supplier_add2 = fields.Char(string='Supplier Address 2')
    supplier_tel = fields.Char(string='Supplier Tel')
    supplier_fax = fields.Char(string='Supplier Fax')
    bill_to_name = fields.Char(string='Bill To Name')
    bill_to_name2 = fields.Char(string='Bill To Name 2')
    bill_to_name3 = fields.Char(string='Bill To Name 3')
    bill_to_add1 = fields.Char(string='Bill To Address 1')
    bill_to_add2 = fields.Char(string='Bill To Address 2')
    notify_add1 = fields.Char(string='Notify Address 1')
    notify_add2 = fields.Char(string='Notify Address 2')
    season = fields.Char(string='Season')
    cus_field1 = fields.Char(string='Custom Field 1')
    end_buyer_account = fields.Char(string='End Buyer Account')
    end_buyer = fields.Char(string='End Buyer')
    inco_terms = fields.Char(string='Incoterms')
    inco_term_desc = fields.Char(string='Incoterm Description')
    payment_mode = fields.Char(string='Payment Mode')
    delivery_address_code = fields.Char(string='Delivery Address Code')
    delivery_address = fields.Char(string='Delivery Address')
    header_text = fields.Char(string='Header Text')
    header_note = fields.Char(string='Header Note')
    order_mode = fields.Char(string='Order Mode')
    company_code = fields.Char(string='Company Code')
    initial_release_date = fields.Date(string='Initial Release Date')
    initial_release_time = fields.Char(string='Initial Release Time')
    final_release_date = fields.Date(string='Final Release Date')
    
    # Fields from LineItem
    purchase_order_item = fields.Char(string='PO Item')
    material_code = fields.Char(string='Material Code')
    vendor_material = fields.Char(string='Vendor Material')
    color_code = fields.Char(string='Color Code')
    color_code_2 = fields.Char(string='Color Code 2')
    ref_material = fields.Char(string='Reference Material')
    ref_material_2 = fields.Char(string='Reference Material 2')
    item_text = fields.Char(string='Item Text')
    mat_po_text = fields.Char(string='Material PO Text')
    page_format = fields.Char(string='Page Format')
    material_description = fields.Char(string='Material Description')
    sales_order1 = fields.Char(string='Sales Order 1')
    sales_order_item = fields.Char(string='Sales Order Item')
    delivery_date1 = fields.Date(string='Delivery Date 1')
    quantity1 = fields.Float(string='Quantity 1')
    uom = fields.Char(string='Unit of Measure')
    net_price1 = fields.Float(string='Net Price 1')
    per = fields.Char(string='Per')
    discount_percentage = fields.Float(string='Discount Percentage')
    discount_value = fields.Float(string='Discount Value')
    net_value1 = fields.Float(string='Net Value 1')
    text = fields.Char(string='Text')
    product_type = fields.Char(string='Product Type')
    gender = fields.Char(string='Gender')
    order_reason = fields.Char(string='Order Reason')
    garment_type = fields.Char(string='Garment Type')
    ptlcode = fields.Char(string='PTL Code')
    ship_mode = fields.Char(string='Ship Mode')
    sales_order_season = fields.Char(string='Sales Order Season')
    buy_year = fields.Char(string='Buy Year')
    brand = fields.Char(string='Brand')
    department_code = fields.Char(string='Department Code')
    emotional_space = fields.Char(string='Emotional Space')
    planning_group = fields.Char(string='Planning Group')
    cpo = fields.Char(string='CPO')
    customer_style = fields.Char(string='Customer Style')
    customer_style_desc = fields.Char(string='Customer Style Description')
    customer_ref1 = fields.Char(string='customer ref1')
    
    # Fields from ScheduleLine
    schedule_line_no = fields.Char(string='Schedule Line No')
    grid_value = fields.Char(string='Size')
    delivery_date = fields.Date(string='Delivery Date')
    sales_order_line = fields.Char(string='Sales Order')
    sales_order_schedule_line = fields.Char(string='Sales Order')
    over_delivery_tolerance = fields.Float(string='Over Delivery Tolerance')
    under_delivery_tolerance = fields.Float(string='Under Delivery Tolerance')
    order_quantity = fields.Float(string='Order Quantity')
    size_quantity = fields.Float(string='Size Quantity')
    net_price = fields.Float(string='Net Price')
    net_value = fields.Float(string='Net Value')
    vendor_material_code = fields.Char(string='Vendor Material Code')
    ex_factory_date = fields.Date(string='Ex-Factory Date')
    additional_sku_no = fields.Char(string='Additional SKU No')
    fg_size = fields.Char(string='FG Size')
    additional_field_1 = fields.Char(string='Additional Field 1')
    additional_field_2 = fields.Char(string='Additional Field 2')

    sku = fields.Char(string='Sku')
    article_num = fields.Char(string='Article Num')
    retail_usd = fields.Char(string='Retail (USD)')
    retail_cad = fields.Char(string='Retail (CAD)')
    retail_gbp = fields.Char(string='Retail (GBP)')
    size_id = fields.Char(string='Size Id')

    # Add the new field
    line_number = fields.Char(string='No', default=1, store=True)

    @api.model
    def create(self, values):
        # Override create method to set the line_number when creating a new record
        lines = self.search([('header_table', '=', values.get('header_table'))])  # Assuming PurchaseorderNum is a reference field to link lines of the same set
        values['line_number'] = len(lines) + 1
        return super(GetPoLines, self).create(values)

    CustomerID = fields.Char(string='Customer Id', related="header_table.CustomerID", store=True)
    AddressID = fields.Char(string='Address Id', related="header_table.DeliveryAddressId", store=True)
    DeliveryAddress = fields.Many2one(string='Delivery Address', related="header_table.DeliveryAddress", store=True)
    additional_ins = fields.Char(string='Additional Instruction', related="header_table.additional_ins_name", store=True)
    care_instruction_set_code = fields.Char(string='Care Intruction Set Code', related="header_table.care_instruction_set_code_2", store=True)

    POwithLine = fields.Char(string ='Po With Lines',  compute ='_compute_po_line', store=True)
    @api.depends('po_number', 'purchase_order_item')
    def _compute_po_line(self):
        for record in self:
            if record.po_number and record.purchase_order_item:
                PurchaseOrderItem_without_zeros = record.purchase_order_item.lstrip('0')
                record.POwithLine = f"{record.po_number}-{PurchaseOrderItem_without_zeros}"
            else:
                record.POwithLine = False

    SoRefLv = fields.Char(string='So Ref Lv', compute="_compute_so_ref_lv", store=True)
    #  Add SLASH SOREFLV TO 
    @api.depends('sales_order_line', 'sales_order_item')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both sales_order and SoOrderItem have values
            if record.sales_order_line and record.sales_order_item:
                # Remove two leading zeros from SoOrderItem and concatenate with sales_order
                so_order_item_without_zeros = record.sales_order_item.lstrip('0')
                record.SoRefLv = f"{record.sales_order_line}/{so_order_item_without_zeros}"
            else:
                record.SoRefLv = False

    size_range = fields.Char(string='Size Range', related="header_table.Size_Range_name", store=True)
    size_lv = fields.Char(string='Lv Size')
    size_mapping = fields.Many2one('size_mapping_lines', string='Size Mapping', compute='_compute_size_mapping', store=True)

    @api.depends('grid_value')
    def _compute_size_mapping(self):
        for record in self:
            size_mapping = self.env['size_mapping_lines'].search([('Size_Range', '=', record.size_range), ('Size', '=', record.grid_value)], limit=1)
            record.size_mapping = size_mapping
            if size_mapping:
                record.size_lv = size_mapping.Size_LV
            else:
                record.size_lv = ''

    ChoosePo = fields.Selection(string='Choose Po', related="header_table.ChoosePo", store=True)
    DelDate = fields.Date(string ="Delivery Date", related="header_table.DelDate", store=True)
    vsd = fields.Char(string='Vsd', related="header_table.vsd", store=True)
    vendor_id = fields.Char(string='Vendor Id', related="header_table.vendor_id", store=True)
    Status = fields.Selection(string='Status', related="header_table.Status", store=True)
    RnNumber = fields.Selection(string='Rn Number', related="header_table.RnNumber", store=True)
    CaNumber = fields.Selection(string='Ca number', related="header_table.CaNumber", store=True)
    ChainID = fields.Many2one(tring='Chain Id', related="header_table.ChainID", store=True)
    color_desc = fields.Char(string='Color Desc', related="header_table.color_desc", store=True)
    style_number = fields.Char(string='Style Number', related="header_table.style_number", store=True)
    FactoryID = fields.Char(string='Factory Id', related="header_table.FactoryID", store=True)
    ProductRef = fields.Char(string = 'Product Ref', related="header_table.ProductRef_name", store=True)
    Collection = fields.Char(string='Collection', related="header_table.Collection_name", store=True)
    silhouette = fields.Char(string='Silhouette', related="header_table.silhouette_name", store=True)
    ItlCode = fields.Char(string='ItlCode', related="header_table.ItlCode_name", store=True)
    Coo = fields.Char(string='Coo', related="header_table.Coo_name", store=True)
    season = fields.Char(string = 'Season', related="header_table.season_name", store=True)
    ChainID_id = fields.Char(string='Chain Id', related="header_table.ChainID_id", store=True)
    ChainID_id_name = fields.Char(string='Chain Id Name', related="header_table.ChainID_id_name", store=True)
    date_of_manufacture = fields.Date(string='Date Manufacture', related="header_table.date_of_manufacture", store=True)
    date_of_manufacture_last_four_letters = fields.Char(string='Date Manufacture', compute='_compute_date_of_manufacture_last_four_letters', store=True)
    Customer_name = fields.Char(string='Customer Name', related="header_table.Customer_name", store=True)

    @api.depends('date_of_manufacture', 'ChainID_id_name')
    def _compute_date_of_manufacture_last_four_letters(self):
        for record in self:
            if record.date_of_manufacture and record.ChainID_id_name:
                month = str(record.date_of_manufacture.month).zfill(2)
                year = str(record.date_of_manufacture.year)[-2:]

                if record.ChainID_id_name == 'VS':
                    record.date_of_manufacture_last_four_letters = month + ' ' + year
                elif record.ChainID_id_name == 'PINK':
                    record.date_of_manufacture_last_four_letters = month + '/' + year
                else:
                    record.date_of_manufacture_last_four_letters = month + year
            else:
                record.date_of_manufacture_last_four_letters = ''

    additional_care_instruction = fields.Char(string="Additional Care Instruction" , related="header_table.additional_care_instruction_name", store=True)
    vss_no = fields.Char(string="Vss")
    vsd_style_6 = fields.Char(string="Vsd Style 6")
    vsd_style_9 = fields.Char(string="Vsd Style 9")



# Main lable
class GetPoLinesMainLable(models.Model):
    _name = 'get_po_mas_lines_main_lable'
    _description = 'Purchase Order Lines Main Lable'

    header_table = fields.Many2one('get_po_mas', string='Purchase Order Reference', ondelete='cascade')
    
    # Fields from PurchaseOrder
    po_number = fields.Char(string='PO Number')
    purchase_order_version = fields.Char(string='PO Version')
    po_date = fields.Date(string='PO Date')
    last_revision_date = fields.Date(string='Last Revision Date')
    currency = fields.Char(string='Currency')
    consignee_name = fields.Char(string='Consignee Name')
    consignee_name2 = fields.Char(string='Consignee Name 2')
    consignee_name3 = fields.Char(string='Consignee Name 3')
    consignee_add1 = fields.Char(string='Consignee Address 1')
    consignee_add2 = fields.Char(string='Consignee Address 2')
    contact_person = fields.Char(string='Contact Person')
    contact_tel = fields.Char(string='Contact Tel')
    contact_email = fields.Char(string='Contact Email')
    supplier_name = fields.Char(string='Supplier Name')
    supplier_add1 = fields.Char(string='Supplier Address 1')
    supplier_add2 = fields.Char(string='Supplier Address 2')
    supplier_tel = fields.Char(string='Supplier Tel')
    supplier_fax = fields.Char(string='Supplier Fax')
    bill_to_name = fields.Char(string='Bill To Name')
    bill_to_name2 = fields.Char(string='Bill To Name 2')
    bill_to_name3 = fields.Char(string='Bill To Name 3')
    bill_to_add1 = fields.Char(string='Bill To Address 1')
    bill_to_add2 = fields.Char(string='Bill To Address 2')
    notify_add1 = fields.Char(string='Notify Address 1')
    notify_add2 = fields.Char(string='Notify Address 2')
    season = fields.Char(string='Season')
    cus_field1 = fields.Char(string='Custom Field 1')
    end_buyer_account = fields.Char(string='End Buyer Account')
    end_buyer = fields.Char(string='End Buyer')
    inco_terms = fields.Char(string='Incoterms')
    inco_term_desc = fields.Char(string='Incoterm Description')
    payment_mode = fields.Char(string='Payment Mode')
    delivery_address_code = fields.Char(string='Delivery Address Code')
    delivery_address = fields.Char(string='Delivery Address')
    header_text = fields.Char(string='Header Text')
    header_note = fields.Char(string='Header Note')
    order_mode = fields.Char(string='Order Mode')
    company_code = fields.Char(string='Company Code')
    initial_release_date = fields.Date(string='Initial Release Date')
    initial_release_time = fields.Char(string='Initial Release Time')
    final_release_date = fields.Date(string='Final Release Date')
    
    # Fields from LineItem
    purchase_order_item = fields.Char(string='PO Item')
    material_code = fields.Char(string='Material Code')
    vendor_material = fields.Char(string='Vendor Material')
    color_code = fields.Char(string='Color Code')
    color_code_2 = fields.Char(string='Color Code 2')
    ref_material = fields.Char(string='Reference Material')
    ref_material_2 = fields.Char(string='Reference Material 2')
    item_text = fields.Char(string='Item Text')
    mat_po_text = fields.Char(string='Material PO Text')
    page_format = fields.Char(string='Page Format')
    material_description = fields.Char(string='Material Description')
    sales_order1 = fields.Char(string='Sales Order 1')
    sales_order_item = fields.Char(string='Sales Order Item')
    delivery_date1 = fields.Date(string='Delivery Date 1')
    quantity1 = fields.Float(string='Quantity 1')
    uom = fields.Char(string='Unit of Measure')
    net_price1 = fields.Float(string='Net Price 1')
    per = fields.Char(string='Per')
    discount_percentage = fields.Float(string='Discount Percentage')
    discount_value = fields.Float(string='Discount Value')
    net_value1 = fields.Float(string='Net Value 1')
    text = fields.Char(string='Text')
    product_type = fields.Char(string='Product Type')
    gender = fields.Char(string='Gender')
    order_reason = fields.Char(string='Order Reason')
    garment_type = fields.Char(string='Garment Type')
    ptlcode = fields.Char(string='PTL Code')
    ship_mode = fields.Char(string='Ship Mode')
    sales_order_season = fields.Char(string='Sales Order Season')
    buy_year = fields.Char(string='Buy Year')
    brand = fields.Char(string='Brand')
    department_code = fields.Char(string='Department Code')
    emotional_space = fields.Char(string='Emotional Space')
    planning_group = fields.Char(string='Planning Group')
    cpo = fields.Char(string='CPO')
    customer_style = fields.Char(string='Customer Style')
    customer_style_desc = fields.Char(string='Customer Style Description')
    customer_ref1 = fields.Char(string='customer ref1')
    
    # Fields from ScheduleLine
    schedule_line_no = fields.Char(string='Schedule Line No')
    grid_value = fields.Char(string='Size')
    delivery_date = fields.Date(string='Delivery Date')
    sales_order_line = fields.Char(string='Sales Order')
    sales_order_schedule_line = fields.Char(string='Sales Order')
    over_delivery_tolerance = fields.Float(string='Over Delivery Tolerance')
    under_delivery_tolerance = fields.Float(string='Under Delivery Tolerance')
    order_quantity = fields.Float(string='Order Quantity')
    size_quantity = fields.Float(string='Size Quantity')
    net_price = fields.Float(string='Net Price')
    net_value = fields.Float(string='Net Value')
    vendor_material_code = fields.Char(string='Vendor Material Code')
    ex_factory_date = fields.Date(string='Ex-Factory Date')
    additional_sku_no = fields.Char(string='Additional SKU No')
    fg_size = fields.Char(string='FG Size')
    additional_field_1 = fields.Char(string='Additional Field 1')
    additional_field_2 = fields.Char(string='Additional Field 2')

    sku = fields.Char(string='Sku')
    article_num = fields.Char(string='Article Num')
    retail_usd = fields.Char(string='Retail (USD)')
    retail_cad = fields.Char(string='Retail (CAD)')
    retail_gbp = fields.Char(string='Retail (GBP)')
    size_id = fields.Char(string='Size Id')

    # Add the new field
    line_number = fields.Char(string='No', default=1, store=True)

    @api.model
    def create(self, values):
        # Override create method to set the line_number when creating a new record
        lines = self.search([('header_table', '=', values.get('header_table'))])  # Assuming PurchaseorderNum is a reference field to link lines of the same set
        values['line_number'] = len(lines) + 1
        return super(GetPoLinesMainLable, self).create(values)

    CustomerID = fields.Char(string='Customer Id', related="header_table.CustomerID", store=True)
    AddressID = fields.Char(string='Address Id', related="header_table.DeliveryAddressId", store=True)
    DeliveryAddress = fields.Many2one(string='Delivery Address', related="header_table.DeliveryAddress", store=True)
    additional_ins = fields.Char(string='Additional Instruction', related="header_table.additional_ins_name", store=True)
    care_instruction_set_code = fields.Char(string='Care Intruction Set Code', related="header_table.care_instruction_set_code_2", store=True)

    POwithLine = fields.Char(string ='Po With Lines',  compute ='_compute_po_line', store=True)
    @api.depends('po_number', 'purchase_order_item')
    def _compute_po_line(self):
        for record in self:
            if record.po_number and record.purchase_order_item:
                PurchaseOrderItem_without_zeros = record.purchase_order_item.lstrip('0')
                record.POwithLine = f"{record.po_number}-{PurchaseOrderItem_without_zeros}"
            else:
                record.POwithLine = False

    SoRefLv = fields.Char(string='So Ref Lv', compute="_compute_so_ref_lv", store=True)
    #  Add SLASH SOREFLV TO 
    @api.depends('sales_order_line', 'sales_order_item')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both sales_order and SoOrderItem have values
            if record.sales_order_line and record.sales_order_item:
                # Remove two leading zeros from SoOrderItem and concatenate with sales_order
                so_order_item_without_zeros = record.sales_order_item.lstrip('0')
                record.SoRefLv = f"{record.sales_order_line}/{so_order_item_without_zeros}"
            else:
                record.SoRefLv = False

    size_range = fields.Char(string='Size Range', related="header_table.Size_Range_name", store=True)
    size_lv = fields.Char(string='Lv Size')
    size_mapping = fields.Many2one('size_mapping_lines', string='Size Mapping', compute='_compute_size_mapping', store=True)

    @api.depends('grid_value')
    def _compute_size_mapping(self):
        for record in self:
            size_mapping = self.env['size_mapping_lines'].search([('Size_Range', '=', record.size_range), ('Size', '=', record.grid_value)], limit=1)
            record.size_mapping = size_mapping
            if size_mapping:
                record.size_lv = size_mapping.Size_LV
            else:
                record.size_lv = ''

    ChoosePo = fields.Selection(string='Choose Po', related="header_table.ChoosePo", store=True)
    DelDate = fields.Date(string ="Delivery Date", related="header_table.DelDate", store=True)
    vsd = fields.Char(string='Vsd', related="header_table.vsd", store=True)
    vendor_id = fields.Char(string='Vendor Id', related="header_table.vendor_id", store=True)
    Status = fields.Selection(string='Status', related="header_table.Status", store=True)
    RnNumber = fields.Selection(string='Rn Number', related="header_table.RnNumber", store=True)
    CaNumber = fields.Selection(string='Ca number', related="header_table.CaNumber", store=True)
    ChainID = fields.Many2one(tring='Chain Id', related="header_table.ChainID", store=True)
    color_desc = fields.Char(string='Color Desc', related="header_table.color_desc", store=True)
    style_number = fields.Char(string='Style Number', related="header_table.style_number", store=True)
    FactoryID = fields.Char(string='Factory Id', related="header_table.FactoryID", store=True)
    ProductRef = fields.Char(string = 'Product Ref', related="header_table.ProductRef_name", store=True)
    Collection = fields.Char(string='Collection', related="header_table.Collection_name", store=True)
    silhouette = fields.Char(string='Silhouette', related="header_table.silhouette_name", store=True)
    ItlCode = fields.Char(string='ItlCode', related="header_table.ItlCode_name", store=True)
    Coo = fields.Char(string='Coo', related="header_table.Coo_name", store=True)
    season = fields.Char(string = 'Season', related="header_table.season_name", store=True)
    ChainID_id = fields.Char(string='Chain Id', related="header_table.ChainID_id", store=True)
    ChainID_id_name = fields.Char(string='Chain Id Name', related="header_table.ChainID_id_name", store=True)
    date_of_manufacture = fields.Date(string='Date Manufacture', related="header_table.date_of_manufacture", store=True)
    date_of_manufacture_last_four_letters = fields.Char(string='Date Manufacture', compute='_compute_date_of_manufacture_last_four_letters', store=True)
    Customer_name = fields.Char(string='Customer Name', related="header_table.Customer_name", store=True)

    @api.depends('date_of_manufacture', 'ChainID_id_name')
    def _compute_date_of_manufacture_last_four_letters(self):
        for record in self:
            if record.date_of_manufacture and record.ChainID_id_name:
                month = str(record.date_of_manufacture.month).zfill(2)
                year = str(record.date_of_manufacture.year)[-2:]

                if record.ChainID_id_name == 'VS':
                    record.date_of_manufacture_last_four_letters = month + ' ' + year
                elif record.ChainID_id_name == 'PINK':
                    record.date_of_manufacture_last_four_letters = month + '/' + year
                else:
                    record.date_of_manufacture_last_four_letters = month + year
            else:
                record.date_of_manufacture_last_four_letters = ''

    additional_care_instruction = fields.Char(string="Additional Care Instruction" , related="header_table.additional_care_instruction_name", store=True)
    vss_no = fields.Char(string="Vss")
    vsd_style_6 = fields.Char(string="Vsd Style 6")
    vsd_style_9 = fields.Char(string="Vsd Style 9")

# Care Lable
class GetPoLinesCareLable(models.Model):
    _name = 'get_po_mas_lines_care_lable'
    _description = 'Purchase Order Lines Main Lable'

    header_table = fields.Many2one('get_po_mas', string='Purchase Order Reference', ondelete='cascade')
    
    # Fields from PurchaseOrder
    po_number = fields.Char(string='PO Number')
    purchase_order_version = fields.Char(string='PO Version')
    po_date = fields.Date(string='PO Date')
    last_revision_date = fields.Date(string='Last Revision Date')
    currency = fields.Char(string='Currency')
    consignee_name = fields.Char(string='Consignee Name')
    consignee_name2 = fields.Char(string='Consignee Name 2')
    consignee_name3 = fields.Char(string='Consignee Name 3')
    consignee_add1 = fields.Char(string='Consignee Address 1')
    consignee_add2 = fields.Char(string='Consignee Address 2')
    contact_person = fields.Char(string='Contact Person')
    contact_tel = fields.Char(string='Contact Tel')
    contact_email = fields.Char(string='Contact Email')
    supplier_name = fields.Char(string='Supplier Name')
    supplier_add1 = fields.Char(string='Supplier Address 1')
    supplier_add2 = fields.Char(string='Supplier Address 2')
    supplier_tel = fields.Char(string='Supplier Tel')
    supplier_fax = fields.Char(string='Supplier Fax')
    bill_to_name = fields.Char(string='Bill To Name')
    bill_to_name2 = fields.Char(string='Bill To Name 2')
    bill_to_name3 = fields.Char(string='Bill To Name 3')
    bill_to_add1 = fields.Char(string='Bill To Address 1')
    bill_to_add2 = fields.Char(string='Bill To Address 2')
    notify_add1 = fields.Char(string='Notify Address 1')
    notify_add2 = fields.Char(string='Notify Address 2')
    season = fields.Char(string='Season')
    cus_field1 = fields.Char(string='Custom Field 1')
    end_buyer_account = fields.Char(string='End Buyer Account')
    end_buyer = fields.Char(string='End Buyer')
    inco_terms = fields.Char(string='Incoterms')
    inco_term_desc = fields.Char(string='Incoterm Description')
    payment_mode = fields.Char(string='Payment Mode')
    delivery_address_code = fields.Char(string='Delivery Address Code')
    delivery_address = fields.Char(string='Delivery Address')
    header_text = fields.Char(string='Header Text')
    header_note = fields.Char(string='Header Note')
    order_mode = fields.Char(string='Order Mode')
    company_code = fields.Char(string='Company Code')
    initial_release_date = fields.Date(string='Initial Release Date')
    initial_release_time = fields.Char(string='Initial Release Time')
    final_release_date = fields.Date(string='Final Release Date')
    
    # Fields from LineItem
    purchase_order_item = fields.Char(string='PO Item')
    material_code = fields.Char(string='Material Code')
    vendor_material = fields.Char(string='Vendor Material')
    color_code = fields.Char(string='Color Code')
    color_code_2 = fields.Char(string='Color Code 2')
    ref_material = fields.Char(string='Reference Material')
    ref_material_2 = fields.Char(string='Reference Material 2')
    item_text = fields.Char(string='Item Text')
    mat_po_text = fields.Char(string='Material PO Text')
    page_format = fields.Char(string='Page Format')
    material_description = fields.Char(string='Material Description')
    sales_order1 = fields.Char(string='Sales Order 1')
    sales_order_item = fields.Char(string='Sales Order Item')
    delivery_date1 = fields.Date(string='Delivery Date 1')
    quantity1 = fields.Float(string='Quantity 1')
    uom = fields.Char(string='Unit of Measure')
    net_price1 = fields.Float(string='Net Price 1')
    per = fields.Char(string='Per')
    discount_percentage = fields.Float(string='Discount Percentage')
    discount_value = fields.Float(string='Discount Value')
    net_value1 = fields.Float(string='Net Value 1')
    text = fields.Char(string='Text')
    product_type = fields.Char(string='Product Type')
    gender = fields.Char(string='Gender')
    order_reason = fields.Char(string='Order Reason')
    garment_type = fields.Char(string='Garment Type')
    ptlcode = fields.Char(string='PTL Code')
    ship_mode = fields.Char(string='Ship Mode')
    sales_order_season = fields.Char(string='Sales Order Season')
    buy_year = fields.Char(string='Buy Year')
    brand = fields.Char(string='Brand')
    department_code = fields.Char(string='Department Code')
    emotional_space = fields.Char(string='Emotional Space')
    planning_group = fields.Char(string='Planning Group')
    cpo = fields.Char(string='CPO')
    customer_style = fields.Char(string='Customer Style')
    customer_style_desc = fields.Char(string='Customer Style Description')
    customer_ref1 = fields.Char(string='customer ref1')
    
    # Fields from ScheduleLine
    schedule_line_no = fields.Char(string='Schedule Line No')
    grid_value = fields.Char(string='Size')
    delivery_date = fields.Date(string='Delivery Date')
    sales_order_line = fields.Char(string='Sales Order')
    sales_order_schedule_line = fields.Char(string='Sales Order')
    over_delivery_tolerance = fields.Float(string='Over Delivery Tolerance')
    under_delivery_tolerance = fields.Float(string='Under Delivery Tolerance')
    order_quantity = fields.Float(string='Order Quantity')
    size_quantity = fields.Float(string='Size Quantity')
    net_price = fields.Float(string='Net Price')
    net_value = fields.Float(string='Net Value')
    vendor_material_code = fields.Char(string='Vendor Material Code')
    ex_factory_date = fields.Date(string='Ex-Factory Date')
    additional_sku_no = fields.Char(string='Additional SKU No')
    fg_size = fields.Char(string='FG Size')
    additional_field_1 = fields.Char(string='Additional Field 1')
    additional_field_2 = fields.Char(string='Additional Field 2')

    sku = fields.Char(string='Sku')
    article_num = fields.Char(string='Article Num')
    retail_usd = fields.Char(string='Retail (USD)')
    retail_cad = fields.Char(string='Retail (CAD)')
    retail_gbp = fields.Char(string='Retail (GBP)')
    size_id = fields.Char(string='Size Id')

    # Add the new field
    line_number = fields.Char(string='No', default=1, store=True)

    @api.model
    def create(self, values):
        # Override create method to set the line_number when creating a new record
        lines = self.search([('header_table', '=', values.get('header_table'))])  # Assuming PurchaseorderNum is a reference field to link lines of the same set
        values['line_number'] = len(lines) + 1
        return super(GetPoLinesCareLable, self).create(values)

    CustomerID = fields.Char(string='Customer Id', related="header_table.CustomerID", store=True)
    AddressID = fields.Char(string='Address Id', related="header_table.DeliveryAddressId", store=True)
    DeliveryAddress = fields.Many2one(string='Delivery Address', related="header_table.DeliveryAddress", store=True)
    additional_ins = fields.Char(string='Additional Instruction', related="header_table.additional_ins_name", store=True)
    care_instruction_set_code = fields.Char(string='Care Intruction Set Code', related="header_table.care_instruction_set_code_2", store=True)

    POwithLine = fields.Char(string ='Po With Lines',  compute ='_compute_po_line', store=True)
    @api.depends('po_number', 'purchase_order_item')
    def _compute_po_line(self):
        for record in self:
            if record.po_number and record.purchase_order_item:
                PurchaseOrderItem_without_zeros = record.purchase_order_item.lstrip('0')
                record.POwithLine = f"{record.po_number}-{PurchaseOrderItem_without_zeros}"
            else:
                record.POwithLine = False

    SoRefLv = fields.Char(string='So Ref Lv', compute="_compute_so_ref_lv", store=True)
    #  Add SLASH SOREFLV TO 
    @api.depends('sales_order_line', 'sales_order_item')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both sales_order and SoOrderItem have values
            if record.sales_order_line and record.sales_order_item:
                # Remove two leading zeros from SoOrderItem and concatenate with sales_order
                so_order_item_without_zeros = record.sales_order_item.lstrip('0')
                record.SoRefLv = f"{record.sales_order_line}/{so_order_item_without_zeros}"
            else:
                record.SoRefLv = False

    size_range = fields.Char(string='Size Range', related="header_table.Size_Range_name", store=True)
    size_lv = fields.Char(string='Lv Size')
    size_mapping = fields.Many2one('size_mapping_lines', string='Size Mapping', compute='_compute_size_mapping', store=True)

    @api.depends('grid_value')
    def _compute_size_mapping(self):
        for record in self:
            size_mapping = self.env['size_mapping_lines'].search([('Size_Range', '=', record.size_range), ('Size', '=', record.grid_value)], limit=1)
            record.size_mapping = size_mapping
            if size_mapping:
                record.size_lv = size_mapping.Size_LV
            else:
                record.size_lv = ''

    ChoosePo = fields.Selection(string='Choose Po', related="header_table.ChoosePo", store=True)
    DelDate = fields.Date(string ="Delivery Date", related="header_table.DelDate", store=True)
    vsd = fields.Char(string='Vsd', related="header_table.vsd", store=True)
    vendor_id = fields.Char(string='Vendor Id', related="header_table.vendor_id", store=True)
    Status = fields.Selection(string='Status', related="header_table.Status", store=True)
    RnNumber = fields.Selection(string='Rn Number', related="header_table.RnNumber", store=True)
    CaNumber = fields.Selection(string='Ca number', related="header_table.CaNumber", store=True)
    ChainID = fields.Many2one(tring='Chain Id', related="header_table.ChainID", store=True)
    color_desc = fields.Char(string='Color Desc', related="header_table.color_desc", store=True)
    style_number = fields.Char(string='Style Number', related="header_table.style_number", store=True)
    FactoryID = fields.Char(string='Factory Id', related="header_table.FactoryID", store=True)
    ProductRef = fields.Char(string = 'Product Ref', related="header_table.ProductRef_name", store=True)
    Collection = fields.Char(string='Collection', related="header_table.Collection_name", store=True)
    silhouette = fields.Char(string='Silhouette', related="header_table.silhouette_name", store=True)
    ItlCode = fields.Char(string='ItlCode', related="header_table.ItlCode_name", store=True)
    Coo = fields.Char(string='Coo', related="header_table.Coo_name", store=True)
    season = fields.Char(string = 'Season', related="header_table.season_name", store=True)
    ChainID_id = fields.Char(string='Chain Id', related="header_table.ChainID_id", store=True)
    ChainID_id_name = fields.Char(string='Chain Id Name', related="header_table.ChainID_id_name", store=True)
    date_of_manufacture = fields.Date(string='Date Manufacture', related="header_table.date_of_manufacture", store=True)
    date_of_manufacture_last_four_letters = fields.Char(string='Date Manufacture', compute='_compute_date_of_manufacture_last_four_letters', store=True)
    Customer_name = fields.Char(string='Customer Name', related="header_table.Customer_name", store=True)

    @api.depends('date_of_manufacture', 'ChainID_id_name')
    def _compute_date_of_manufacture_last_four_letters(self):
        for record in self:
            if record.date_of_manufacture and record.ChainID_id_name:
                month = str(record.date_of_manufacture.month).zfill(2)
                year = str(record.date_of_manufacture.year)[-2:]

                if record.ChainID_id_name == 'VS':
                    record.date_of_manufacture_last_four_letters = month + ' ' + year
                elif record.ChainID_id_name == 'PINK':
                    record.date_of_manufacture_last_four_letters = month + '/' + year
                else:
                    record.date_of_manufacture_last_four_letters = month + year
            else:
                record.date_of_manufacture_last_four_letters = ''

    additional_care_instruction = fields.Char(string="Additional Care Instruction" , related="header_table.additional_care_instruction_name", store=True)
    vss_no = fields.Char(string="Vss")
    vsd_style_6 = fields.Char(string="Vsd Style 6")
    vsd_style_9 = fields.Char(string="Vsd Style 9")


class GetPoLinesPriceTkt(models.Model):
    _name = 'get_po_mas_lines_price_tkt'
    _description = 'Purchase Order Lines Price Tkt'

    header_table = fields.Many2one('get_po_mas', string='Purchase Order Reference', ondelete='cascade')
    
    # Fields from PurchaseOrder
    po_number = fields.Char(string='PO Number')
    purchase_order_version = fields.Char(string='PO Version')
    po_date = fields.Date(string='PO Date')
    last_revision_date = fields.Date(string='Last Revision Date')
    currency = fields.Char(string='Currency')
    consignee_name = fields.Char(string='Consignee Name')
    consignee_name2 = fields.Char(string='Consignee Name 2')
    consignee_name3 = fields.Char(string='Consignee Name 3')
    consignee_add1 = fields.Char(string='Consignee Address 1')
    consignee_add2 = fields.Char(string='Consignee Address 2')
    contact_person = fields.Char(string='Contact Person')
    contact_tel = fields.Char(string='Contact Tel')
    contact_email = fields.Char(string='Contact Email')
    supplier_name = fields.Char(string='Supplier Name')
    supplier_add1 = fields.Char(string='Supplier Address 1')
    supplier_add2 = fields.Char(string='Supplier Address 2')
    supplier_tel = fields.Char(string='Supplier Tel')
    supplier_fax = fields.Char(string='Supplier Fax')
    bill_to_name = fields.Char(string='Bill To Name')
    bill_to_name2 = fields.Char(string='Bill To Name 2')
    bill_to_name3 = fields.Char(string='Bill To Name 3')
    bill_to_add1 = fields.Char(string='Bill To Address 1')
    bill_to_add2 = fields.Char(string='Bill To Address 2')
    notify_add1 = fields.Char(string='Notify Address 1')
    notify_add2 = fields.Char(string='Notify Address 2')
    season = fields.Char(string='Season')
    cus_field1 = fields.Char(string='Custom Field 1')
    end_buyer_account = fields.Char(string='End Buyer Account')
    end_buyer = fields.Char(string='End Buyer')
    inco_terms = fields.Char(string='Incoterms')
    inco_term_desc = fields.Char(string='Incoterm Description')
    payment_mode = fields.Char(string='Payment Mode')
    delivery_address_code = fields.Char(string='Delivery Address Code')
    delivery_address = fields.Char(string='Delivery Address')
    header_text = fields.Char(string='Header Text')
    header_note = fields.Char(string='Header Note')
    order_mode = fields.Char(string='Order Mode')
    company_code = fields.Char(string='Company Code')
    initial_release_date = fields.Date(string='Initial Release Date')
    initial_release_time = fields.Char(string='Initial Release Time')
    final_release_date = fields.Date(string='Final Release Date')
    
    # Fields from LineItem
    purchase_order_item = fields.Char(string='PO Item')
    material_code = fields.Char(string='Material Code')
    vendor_material = fields.Char(string='Vendor Material')
    color_code = fields.Char(string='Color Code')
    color_code_2 = fields.Char(string='Color Code 2')
    ref_material = fields.Char(string='Reference Material')
    ref_material_2 = fields.Char(string='Reference Material 2')
    item_text = fields.Char(string='Item Text')
    mat_po_text = fields.Char(string='Material PO Text')
    page_format = fields.Char(string='Page Format')
    material_description = fields.Char(string='Material Description')
    sales_order1 = fields.Char(string='Sales Order 1')
    sales_order_item = fields.Char(string='Sales Order Item')
    delivery_date1 = fields.Date(string='Delivery Date 1')
    quantity1 = fields.Float(string='Quantity 1')
    uom = fields.Char(string='Unit of Measure')
    net_price1 = fields.Float(string='Net Price 1')
    per = fields.Char(string='Per')
    discount_percentage = fields.Float(string='Discount Percentage')
    discount_value = fields.Float(string='Discount Value')
    net_value1 = fields.Float(string='Net Value 1')
    text = fields.Char(string='Text')
    product_type = fields.Char(string='Product Type')
    gender = fields.Char(string='Gender')
    order_reason = fields.Char(string='Order Reason')
    garment_type = fields.Char(string='Garment Type')
    ptlcode = fields.Char(string='PTL Code')
    ship_mode = fields.Char(string='Ship Mode')
    sales_order_season = fields.Char(string='Sales Order Season')
    buy_year = fields.Char(string='Buy Year')
    brand = fields.Char(string='Brand')
    department_code = fields.Char(string='Department Code')
    emotional_space = fields.Char(string='Emotional Space')
    planning_group = fields.Char(string='Planning Group')
    cpo = fields.Char(string='CPO')
    customer_style = fields.Char(string='Customer Style')
    customer_style_desc = fields.Char(string='Customer Style Description')
    customer_ref1 = fields.Char(string='customer ref1')
    
    # Fields from ScheduleLine
    schedule_line_no = fields.Char(string='Schedule Line No')
    grid_value = fields.Char(string='Size')
    delivery_date = fields.Date(string='Delivery Date')
    sales_order_line = fields.Char(string='Sales Order')
    sales_order_schedule_line = fields.Char(string='Sales Order')
    over_delivery_tolerance = fields.Float(string='Over Delivery Tolerance')
    under_delivery_tolerance = fields.Float(string='Under Delivery Tolerance')
    order_quantity = fields.Float(string='Order Quantity')
    size_quantity = fields.Float(string='Size Quantity')
    net_price = fields.Float(string='Net Price')
    net_value = fields.Float(string='Net Value')
    vendor_material_code = fields.Char(string='Vendor Material Code')
    ex_factory_date = fields.Date(string='Ex-Factory Date')
    additional_sku_no = fields.Char(string='Additional SKU No')
    fg_size = fields.Char(string='FG Size')
    additional_field_1 = fields.Char(string='Additional Field 1')
    additional_field_2 = fields.Char(string='Additional Field 2')

    sku = fields.Char(string='Sku')
    article_num = fields.Char(string='Article Num')
    retail_usd = fields.Char(string='Retail (USD)')
    retail_cad = fields.Char(string='Retail (CAD)')
    retail_gbp = fields.Char(string='Retail (GBP)')
    size_id = fields.Char(string='Size Id')

    # Add the new field
    line_number = fields.Char(string='No', default=1, store=True)

    @api.model
    def create(self, values):
        # Override create method to set the line_number when creating a new record
        lines = self.search([('header_table', '=', values.get('header_table'))])  # Assuming PurchaseorderNum is a reference field to link lines of the same set
        values['line_number'] = len(lines) + 1
        return super(GetPoLinesPriceTkt, self).create(values)

    CustomerID = fields.Char(string='Customer Id', related="header_table.CustomerID", store=True)
    AddressID = fields.Char(string='Address Id', related="header_table.DeliveryAddressId", store=True)
    DeliveryAddress = fields.Many2one(string='Delivery Address', related="header_table.DeliveryAddress", store=True)
    additional_ins = fields.Char(string='Additional Instruction', related="header_table.additional_ins_name", store=True)
    care_instruction_set_code = fields.Char(string='Care Intruction Set Code', related="header_table.care_instruction_set_code_2", store=True)

    POwithLine = fields.Char(string ='Po With Lines',  compute ='_compute_po_line', store=True)
    @api.depends('po_number', 'purchase_order_item')
    def _compute_po_line(self):
        for record in self:
            if record.po_number and record.purchase_order_item:
                PurchaseOrderItem_without_zeros = record.purchase_order_item.lstrip('0')
                record.POwithLine = f"{record.po_number}-{PurchaseOrderItem_without_zeros}"
            else:
                record.POwithLine = False

    SoRefLv = fields.Char(string='So Ref Lv', compute="_compute_so_ref_lv", store=True)
    #  Add SLASH SOREFLV TO 
    @api.depends('sales_order_line', 'sales_order_item')
    def _compute_so_ref_lv(self):
        for record in self:
            # Check if both sales_order and SoOrderItem have values
            if record.sales_order_line and record.sales_order_item:
                # Remove two leading zeros from SoOrderItem and concatenate with sales_order
                so_order_item_without_zeros = record.sales_order_item.lstrip('0')
                record.SoRefLv = f"{record.sales_order_line}/{so_order_item_without_zeros}"
            else:
                record.SoRefLv = False

    size_range = fields.Char(string='Size Range', related="header_table.Size_Range_name", store=True)
    size_lv = fields.Char(string='Lv Size')
    size_mapping = fields.Many2one('size_mapping_lines', string='Size Mapping', compute='_compute_size_mapping', store=True)

    @api.depends('grid_value')
    def _compute_size_mapping(self):
        for record in self:
            size_mapping = self.env['size_mapping_lines'].search([('Size_Range', '=', record.size_range), ('Size', '=', record.grid_value)], limit=1)
            record.size_mapping = size_mapping
            if size_mapping:
                record.size_lv = size_mapping.Size_LV
            else:
                record.size_lv = ''

    ChoosePo = fields.Selection(string='Choose Po', related="header_table.ChoosePo", store=True)
    DelDate = fields.Date(string ="Delivery Date", related="header_table.DelDate", store=True)
    vsd = fields.Char(string='Vsd', related="header_table.vsd", store=True)
    vendor_id = fields.Char(string='Vendor Id', related="header_table.vendor_id", store=True)
    Status = fields.Selection(string='Status', related="header_table.Status", store=True)
    RnNumber = fields.Selection(string='Rn Number', related="header_table.RnNumber", store=True)
    CaNumber = fields.Selection(string='Ca number', related="header_table.CaNumber", store=True)
    ChainID = fields.Many2one(tring='Chain Id', related="header_table.ChainID", store=True)
    color_desc = fields.Char(string='Color Desc', related="header_table.color_desc", store=True)
    style_number = fields.Char(string='Style Number', related="header_table.style_number", store=True)
    FactoryID = fields.Char(string='Factory Id', related="header_table.FactoryID", store=True)
    ProductRef = fields.Char(string = 'Product Ref', related="header_table.ProductRef_name", store=True)
    Collection = fields.Char(string='Collection', related="header_table.Collection_name", store=True)
    silhouette = fields.Char(string='Silhouette', related="header_table.silhouette_name", store=True)
    ItlCode = fields.Char(string='ItlCode', related="header_table.ItlCode_name", store=True)
    Coo = fields.Char(string='Coo', related="header_table.Coo_name", store=True)
    season = fields.Char(string = 'Season', related="header_table.season_name", store=True)
    ChainID_id = fields.Char(string='Chain Id', related="header_table.ChainID_id", store=True)
    ChainID_id_name = fields.Char(string='Chain Id Name', related="header_table.ChainID_id_name", store=True)
    date_of_manufacture = fields.Date(string='Date Manufacture', related="header_table.date_of_manufacture", store=True)
    date_of_manufacture_last_four_letters = fields.Char(string='Date Manufacture', compute='_compute_date_of_manufacture_last_four_letters', store=True)
    Customer_name = fields.Char(string='Customer Name', related="header_table.Customer_name", store=True)

    @api.depends('date_of_manufacture', 'ChainID_id_name')
    def _compute_date_of_manufacture_last_four_letters(self):
        for record in self:
            if record.date_of_manufacture and record.ChainID_id_name:
                month = str(record.date_of_manufacture.month).zfill(2)
                year = str(record.date_of_manufacture.year)[-2:]

                if record.ChainID_id_name == 'VS':
                    record.date_of_manufacture_last_four_letters = month + ' ' + year
                elif record.ChainID_id_name == 'PINK':
                    record.date_of_manufacture_last_four_letters = month + '/' + year
                else:
                    record.date_of_manufacture_last_four_letters = month + year
            else:
                record.date_of_manufacture_last_four_letters = ''

    additional_care_instruction = fields.Char(string="Additional Care Instruction" , related="header_table.additional_care_instruction_name", store=True)
    vss_no = fields.Char(string="Vss")
    vsd_style_6 = fields.Char(string="Vsd Style 6")
    vsd_style_9 = fields.Char(string="Vsd Style 9")