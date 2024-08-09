import requests
import base64
from io import BytesIO
import xlrd
from xml.etree import ElementTree as ET
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import zeep
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET
from xml.dom import minidom


class GetPo(models.Model):
    _name = 'get_po_mas'
    _description = 'Purchase Order'
    _rec_name = 'order_number'

    order_number = fields.Char(string='Order Number', required=True)
    line_ids = fields.One2many('get_po_mas_lines', 'header_table', string='Order Lines')
    pdm = fields.Selection([('PDM300', 'PDM300'), ('PSI100', 'PSI100')],
                              string='System', default='PDM300')
    ChoosePo = fields.Selection([('RFID', 'RFID'), ('CARE LABELS', 'CARE LABELS'), ('PRICE TKT / BARCODE STK', 'PRICE TKT / BARCODE STK'), ('MAIN LABELS', 'MAIN LABELS')],
                              string='Choose Po', default='RFID')
    DelDate = fields.Date(string ="Delivery Date")
    vsd = fields.Char(string='Vsd')
    vendor_id = fields.Char(string='Vendor Id')
    Status = fields.Selection([('Success', 'Success'), ('Open', 'Open'), ('Cancelled', 'Cancelled'), ('Progress', 'Progress')],
                              string='Status', default='Open')
    RnNumber = fields.Selection([('54867', '54867')],
                              string='Rn Number', default='54867')
    CaNumber = fields.Selection([('67359', '67359')],
                              string='Ca number', default='67359')
    ChainID = fields.Many2one('chain_master',string='Chain Id', store=True)
    ChainID_id = fields.Char(string='Chain Id', compute = '_compute_chain_id', store=True)

    @api.model
    def compute_total_orders(self):
        total_orders = {
            'total_orders': len(self.search([])),
            'all_total_order': len(self.search([])),
            'success': len(self.search([("Status", "=", "Success")])),
        }
        return total_orders


    @api.depends('ChainID')
    def _compute_chain_id(self):
        for record in self:
            if record.ChainID:
                record.ChainID_id = record.ChainID.ChainId
            else:
                record.ChainID_id = False

    ChainID_id_name = fields.Char(string='Chain Id Name', compute = '_compute_chain_id_name', store=True)
    @api.depends('ChainID')
    def _compute_chain_id_name(self):
        for record in self:
            if record.ChainID:
                record.ChainID_id_name = record.ChainID.ChainName
            else:
                record.ChainID_id_name = False
                
    color_desc = fields.Char(string='Color Desc')
    style_number = fields.Char(string='Style Number')
    FactoryID = fields.Char(string='Factory Id')

    ProductRef = fields.Many2one('product_reference_master' , string = 'Product Ref')
    ProductRef_name = fields.Char(string='Product Ref', compute='_compute_PRODUCT_REF_name')
    @api.depends('ProductRef')
    def _compute_PRODUCT_REF_name(self):
        for record in self:
            if record.ProductRef:
                record.ProductRef_name = record.ProductRef.ProductRef_name
            else:
                record.ProductRef_name = False

    Collection = fields.Many2one('collection_master' , string='Collection')
    Collection_name = fields.Char(string='Collection', compute='_compute_collection')
    @api.depends('Collection')
    def _compute_collection(self):
        for record in self:
            if record.Collection:
                record.Collection_name = record.Collection.Collection_name
            else:
                record.Collection_name = False

    silhouette = fields.Many2one('silhouette_master', string='Silhouette')
    silhouette_name = fields.Char(string='Silhouette', compute='_compute_silhouette')
    @api.depends('silhouette')
    def _compute_silhouette(self):
        for record in self:
            if record.silhouette:
                record.silhouette_name = record.silhouette.silhouette_name
            else:
                record.silhouette_name = False

    ItlCode = fields.Many2one('itl_code', string='ItlCode')
    ItlCode_name = fields.Char(string='ItlCode', compute='_compute_ItlCode')
    @api.depends('ItlCode')
    def _compute_ItlCode(self):
        for record in self:
            if record.ItlCode:
                record.ItlCode_name = record.ItlCode.ItlCode_Name
            else:
                record.ItlCode_name = False

    '''Coo Details'''
    Coo = fields.Many2one('coo_master',string='Coo')
    Coo_name = fields.Char(string='Coo', compute='_compute_coo')
    @api.depends('Coo')
    def _compute_coo(self):
        for record in self:
            if record.Coo:
                record.Coo_name = record.Coo.coo_name
            else:
                record.Coo_name = False

    '''Season Details'''
    season = fields.Many2one('seson_master' , string = 'Season')
    season_name = fields.Char(string='Season', compute='_compute_season_name')
    @api.depends('season')
    def _compute_season_name(self):
        for record in self:
            if record.season:
                record.season_name = record.season.season_name
            else:
                record.season_name = False

    '''Customer Details and Delivery address Details'''
    Customer = fields.Many2one('res.partner',string='Customer', store=True)
    Customer_name = fields.Char(string='Customer Name', compute = '_compute_customer_name')
    @api.depends('Customer')
    def _compute_customer_name(self):
        for record in self:
            if record.Customer:
                record.Customer_name = record.Customer.name
            else:
                record.Customer_name = False
    DeliveryAddress = fields.Many2one('res.partner', string='Delivery Address',
                                      domain="[('id', 'child_of', Customer)]")

    @api.onchange('Customer')
    def onchange_customer(self):
        if self.Customer:
            # Set DeliveryAddress domain to show only addresses related to the selected customer
            return {'domain': {'DeliveryAddress': [('id', 'child_of', self.Customer.id)]}}
        else:
            return {'domain': {'DeliveryAddress': []}}

    DeliveryAddressId = fields.Char(string='Delivery Address Id', compute='_compute_d_add_id', store=True)
    @api.depends('DeliveryAddress')
    def _compute_d_add_id(self):
        for record in self:
            if record.DeliveryAddress:
                record.DeliveryAddressId = record.DeliveryAddress.phone
            else:
                record.DeliveryAddressId = False

    AddressID = fields.Char(string='Address Id', compute = '_compute_a_id', store=True)
    @api.depends('Customer')
    def _compute_a_id(self):
        for record in self:
            if record.Customer:
                record.AddressID = record.Customer.mobile
            else:
                record.AddressID = False

    CustomerID = fields.Char(string='Customer Id', compute = '_compute_c_id', store=True)
    @api.depends('Customer')
    def _compute_c_id(self):
        for record in self:
            if record.Customer:
                record.CustomerID = record.Customer.vat
            else:
                record.CustomerID = False
                

    '''Date of Manu'''
    date_of_manufacture = fields.Date(string='Date Manufacture')

    @api.depends('date_of_manufactur')
    def _compute_last_four_letters(self):
        for record in self:
            if record.Dateofmanu:
                month = str(record.Dateofmanu.month).zfill(2)  # Ensure two digits for the day
                year = str(record.Dateofmanu.year)[-2:]  # Extract last two digits of the year
                record.date = month + ' ' + year
            else:
                record.date = ''

    '''Size Data'''
    size_range = fields.Many2one('size_range_master', string='Size Range')
    Size_Range_name = fields.Char(string='Size Range', compute ='_compute_size_range_name' , store=True)
    @api.depends('size_range')
    def _compute_size_range_name(self):
        for record in self:
            if record.size_range:
                record.Size_Range_name = record.size_range.Size_Range_name
            else:
                record.Size_Range_name = ''
                
    '''Care Instructions'''
    additional_ins = fields.Many2one('additional_instruction_master' , string = 'Additional Instruction')
    additional_ins_name = fields.Char(string='Additional Instruction', compute='_compute_additional_ins')
    @api.depends('additional_ins')
    def _compute_additional_ins(self):
        for record in self:
            if record.additional_ins:
                record.additional_ins_name = record.additional_ins.additional_ins_name
            else:
                record.additional_ins_name = False

    care_instruction_set_code = fields.Many2one('care_instruction_set_code_master', string='Care Intruction Set Code')
    care_instruction_set_code_2 = fields.Char(string='Care Intruction Set Code', compute = '_compute_care_instruction_set_code_2')
    @api.depends('care_instruction_set_code')
    def _compute_care_instruction_set_code_2(self):
        for record in self:
            if record.care_instruction_set_code:
                record.care_instruction_set_code_2 = record.care_instruction_set_code.care_instruction_set_code_2
            else:
                record.care_instruction_set_code_2 = False


    '''Get Po Details'''
    def fetch_po_data(self):
        if self.line_ids:
            raise UserError(_('Data already fetched. Cannot perform operation again.'))
        url = 'https://nwportal.masholdings.com/POXMLDownload/Config1?wsdl'
        headers = {'Content-Type': 'text/xml'}
        
        soap_request = f"""
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:pod="http://sap.com/podown/">
           <soapenv:Header/>
           <soapenv:Body>
              <pod:getPO>
                 <PO>{self.order_number}</PO>
                 <Frdt>01.01.2020</Frdt>
                 <Todt>31.12.2099</Todt>
                 <IUser>V_PoornimaJa</IUser>
                 <IPass>ITL@$OE@2o23</IPass>
                 <MerName></MerName>
                 <MerEmail></MerEmail>
                 <Rev></Rev>
                 <system>{self.pdm}</system>
              </pod:getPO>
           </soapenv:Body>
        </soapenv:Envelope>
        """
        try:
            response = requests.post(url, data=soap_request, headers=headers)
            response.raise_for_status()
        except requests.exceptions.RequestException:
            raise UserError("Check your internet connection and try again.")

        if response.status_code == 200:
            response_xml = response.content.decode('utf-8')
            
            try:
                root = ET.fromstring(response_xml)
                encoded_data_tag = root.find(".//return")
                
                if encoded_data_tag is not None:
                    encoded_data = encoded_data_tag.text
                    decoded_data = base64.b64decode(encoded_data)
                    decoded_xml_string = decoded_data.decode("utf-8")
                    decoded_root = ET.fromstring(decoded_xml_string)
                    
                    if not decoded_root.findall('.//PurchaseOrder'):
                        raise UserError(f"No Purchase Order found for the given number: {self.order_number}")
                    
                    self.line_ids.unlink()
                    lines_to_create = []

                    def valid_date(date_str):
                        try:
                            if date_str and date_str != "0000-00-00":
                                return date_str
                        except ValueError:
                            pass
                        return None
                    
                    for order in decoded_root.findall('.//PurchaseOrder'):
                        order_values = {
                            'header_table': self.id,
                            'po_number': order.findtext("PurchaseOrderNumber", default=""),
                            'purchase_order_version': order.findtext("PurchaseOrderVersion", default=""),
                            'po_date': valid_date(order.findtext("PurchaseOrderDate", default="")),
                            'consignee_name': order.findtext("ConsigneeName", default=""),
                            'consignee_name2': order.findtext("ConsigneeName2", default=""),
                            'consignee_name3': order.findtext("ConsigneeName3", default=""),
                            'consignee_add1': order.findtext("ConsigneeAdd1", default=""),
                            'consignee_add2': order.findtext("ConsigneeAdd2", default=""),
                            'contact_person': order.findtext("ContactPerson", default=""),
                            'contact_tel': order.findtext("ContactTel", default=""),
                            'contact_email': order.findtext("ContactEMail", default=""),
                            'supplier_name': order.findtext("SupplierName", default=""),
                            'supplier_add1': order.findtext("SupplierAdd1", default=""),
                            'supplier_add2': order.findtext("SupplierAdd2", default=""),
                            'supplier_tel': order.findtext("SupplierTel", default=""),
                            'supplier_fax': order.findtext("SupplierFax", default=""),
                            'bill_to_name': order.findtext("BillToName", default=""),
                            'bill_to_name2': order.findtext("BillToName2", default=""),
                            'bill_to_name3': order.findtext("BillToName3", default=""),
                            'bill_to_add1': order.findtext("BillToAdd1", default=""),
                            'bill_to_add2': order.findtext("BillToAdd2", default=""),
                            'notify_add1': order.findtext("NotifyAdd1", default=""),
                            'notify_add2': order.findtext("NotifyAdd2", default=""),
                            'season': order.findtext("Season", default=""),
                            'cus_field1': order.findtext("CusField1", default=""),
                            'end_buyer_account': order.findtext("EndBuyerAccnt", default=""),
                            'end_buyer': order.findtext("EndBuyer", default=""),
                            'inco_terms': order.findtext("IncoTerms", default=""),
                            'inco_term_desc': order.findtext("IncoTermDesc", default=""),
                            'payment_mode': order.findtext("PaymentMode", default=""),
                            'delivery_address_code': order.findtext("DeliveryAddressCode", default=""),
                            'delivery_address': order.findtext("DeliveryAddress", default=""),
                            'header_text': order.findtext("HeaderText", default=""),
                            'header_note': order.findtext("HeaderNote", default=""),
                            'order_mode': order.findtext("OrderMode", default=""),
                            'company_code': order.findtext("CompanyCode", default=""),
                            'initial_release_date': valid_date(order.findtext("InitialReleaseDate", default="")),
                            'initial_release_time': order.findtext("InitialReleaseTime", default=""),
                            'final_release_date': valid_date(order.findtext("FinalReleaseDate", default="")),
                        }

                        line_items = order.find("LineItems").findall("LineItem")
                        for line_item in line_items:
                            line_values = {
                                **order_values,
                                'purchase_order_item': line_item.findtext("PurchaseOrderItem", default=""),
                                'material_code': line_item.findtext("MaterialCode", default=""),
                                'vendor_material': line_item.findtext("VendorMaterial", default=""),
                                'color_code': line_item.findtext("ColorCode", default=""),
                                'color_code_2': line_item.findtext("FinishedGoodColorCode", default=""),
                                'ref_material': line_item.findtext("RefMaterial", default=""),
                                'ref_material_2': line_item.findtext("RefMaterial2", default=""),
                                'item_text': line_item.findtext("ItemText", default=""),
                                'mat_po_text': line_item.findtext("MatPoText", default=""),
                                'page_format': line_item.findtext("PageFormat", default=""),
                                'material_description': line_item.findtext("MaterialDescription", default=""),
                                'sales_order_line': line_item.findtext("SalesOrder", default=""),
                                'sales_order_item': line_item.findtext("SalesOrderItem", default=""),
                                'delivery_date': valid_date(line_item.findtext("DeliveryDate", default="")),
                                'order_quantity': float(line_item.findtext("Quantity", '0').strip() or 0),
                                'uom': line_item.findtext("UOM", default=""),
                                'net_price': float(line_item.findtext("NetPrice", '0').strip() or 0),
                                'net_value': float(line_item.findtext("NetValue", '0').strip() or 0),
                                'per': line_item.findtext("Per", default=""),
                                'discount_percentage': float(line_item.findtext("DiscountPercentage", '0').strip() or 0),
                                'discount_value': float(line_item.findtext("DiscountValue", '0').strip() or 0),
                                'text': line_item.findtext("Text", default=""),
                                'product_type': line_item.findtext("ProductType", default=""),
                                'gender': line_item.findtext("Gender", default=""),
                                'order_reason': line_item.findtext("OrderReason", default=""),
                                'garment_type': line_item.findtext("GarmentType", default=""),
                                'ptlcode': line_item.findtext("PTLcode", default=""),
                                'ship_mode': line_item.findtext("ShipMode", default=""),
                                'sales_order_season': line_item.findtext("SalesOrderSeason", default=""),
                                'buy_year': line_item.findtext("BuyYear", default=""),
                                'brand': line_item.findtext("Brand", default=""),
                                'department_code': line_item.findtext("DepartmentCode", default=""),
                                'emotional_space': line_item.findtext("EmotionalSpace", default=""),
                                'planning_group': line_item.findtext("PlanningGroup", default=""),
                                'cpo': line_item.findtext("CPO", default=""),
                                'ex_factory_date': valid_date(line_item.findtext("ExFactoryDate", default="")),
                                'customer_style': line_item.findtext("CustomerStyle", default=""),
                                'customer_style_desc': line_item.findtext("CustomerStyleDesc", default=""),
                                'customer_ref1': line_item.findtext("CustomerRef1", default=""),
                            }
                            
                            schedule_lines = line_item.find("ScheduleLines").findall("ScheduleLine")
                            for schedule_line in schedule_lines:
                                schedule_line_values = {
                                    'schedule_line_no': schedule_line.findtext("ScheduleLineNo", default=""),
                                    'grid_value': schedule_line.findtext("GridValue", default=""),
                                    'delivery_date': valid_date(schedule_line.findtext("DeliveryDate", default="")),
                                    'sales_order_schedule_line': schedule_line.findtext("SalesOrder", default=""),
                                    'over_delivery_tolerance': float(schedule_line.findtext("OverDeliveryTolerance", '0').strip() or 0),
                                    'under_delivery_tolerance': float(schedule_line.findtext("UnderDeliveryTolerance", '0').strip() or 0),
                                    'size_quantity': float(schedule_line.findtext("Quantity", '0').strip() or 0),
                                    'net_price': float(schedule_line.findtext("NetPrice", '0').strip() or 0),
                                    'net_value': float(schedule_line.findtext("NetValue", '0').strip() or 0),
                                    'vendor_material_code': schedule_line.findtext("VendorMaterialCode", default=""),
                                    'ex_factory_date': valid_date(schedule_line.findtext("ExFactoryDate", default="")),
                                    'additional_sku_no': schedule_line.findtext("AdditionalSKUNo", default=""),
                                    'fg_size': schedule_line.findtext("FGSize", default=""),
                                    'additional_field_1': schedule_line.findtext("AdditionalField1", default=""),
                                    'additional_field_2': schedule_line.findtext("AdditionalField2", default=""),
                                }

                                final_values = {**line_values, **schedule_line_values}
                                lines_to_create.append(final_values)
                    
                    self.env['get_po_mas_lines'].create(lines_to_create)
                    message = _("RECEIVED SUCCESSFULLY.")
                    return {
                        'type': 'ir.actions.client',
                        'tag': 'display_notification',
                        'params': {
                            'message': message,
                            'type': 'success',
                            'sticky': True,
                            'next': {
                                'type': 'ir.actions.client',
                                'tag': 'reload',
                            }
                        }
                    }
                    # return {
                    #     'effect': {
                    #         'fadeout': 'slow',
                    #         'message': 'Data fetched and stored successfully.',
                    #         'type': 'rainbow_man',
                    #     }
                    # }
                    
                else:
                    raise UserError(f"Failed to retrieve Purchase Order data for the given number: {self.order_number}")
            except ET.ParseError:
                raise UserError(f"{decoded_xml_string}")
        else:
            raise UserError(f"Error: {response.status_code}\n{response.reason}")
            

    def delete_records_from_related_model(self):
        if not self.order_number:
            raise UserError(_('Please provide a PO Number for deleting records.'))

        # Assuming lbx_mi_gpo_d001 is the related model
        gpo_d001_model = self.env['get_po_mas_lines']

        # Find records based on PoNumber
        records_to_delete = gpo_d001_model.search([('po_number', '=', self.order_number)])

        if not records_to_delete:
            raise UserError(_('No records found with PO Number %s' % self.order_number))

        # Delete the records in the related model
        records_to_delete.unlink()

        # Check if any records were deleted
        if records_to_delete:
            # Notification for success
            message = _("PO deleted successfully.")
            return {
                'type': 'ir.actions.client',
                'tag': 'display_notification',
                'params': {
                    'message': message,
                    'type': 'danger',
                    'sticky': True,
                    'next': {
                        'type': 'ir.actions.client',
                        'tag': 'reload',
                    }
                }
            }
        else:
            # No records deleted, show a different message or do nothing
            return {'type': 'ir.actions.do_nothing'}

    selected_vpo_details = fields.Many2one('get_vpo_mas', string='Select Vpo')
    color_code_2 = fields.Char(string='Color Code 2', related="line_ids.color_code_2")

    def compare_and_extract_data(self):
        if not self.line_ids:
            raise ValidationError(_('There Is No Data To Match'))

        if not self.selected_vpo_details:
            raise ValidationError(_('Please select the VPO details before comparing and extracting data.'))

        VPO = self.env['get_vpo_mas_lines']

        missing_records_details = []

        # Iterate through existing records and update values
        for existing_record in self.line_ids:
            # Find data based on matching criteria
            data = VPO.search([
                ('po_number', '=', existing_record.po_number),
                ('size_lv', '=', existing_record.grid_value),
                ('style', '=', existing_record.customer_style),
            ])

            new_values = self._extract_po_line_values(data, existing_record.color_code_2)

            if not self.color_code_2:
                raise ValidationError(_('Color Code Missing.'))

            if new_values:
                existing_record.write(dict(new_values))
            else:
                missing_records_details.append({
                    'line_number': existing_record.line_number,
                    'details': {
                        'PoNumber': existing_record.po_number,
                        'Size': existing_record.grid_value,
                        'Style': existing_record.customer_style,
                        'ColorCode': existing_record.color_code_2,
                    },
                    'reason': 'For This Po Records Matching criteria not found in VPO.',
                })

        if missing_records_details:
            error_message = "Data not transferred for the following line numbers:\n"
            for record_details in missing_records_details:
                error_message += (
                    f"Line Number: {record_details['line_number']}, "
                    f"Details: {record_details['details']}, "
                    f"Reason: {record_details['reason']}\n"
                )

            raise UserError(error_message)

        # Display success message and reload the view
        message = _("Data fetched and updated successfully.")
        return {
            'type': 'ir.actions.client',
            'tag': 'display_notification',
            'params': {
                'message': message,
                'type': 'success',
                'sticky': True,
                'next': {
                    'type': 'ir.actions.client',
                    'tag': 'reload',
                }
            }
        }
            
    def _extract_po_line_values(self, data, existing_color_code):
        # Extract and return values for each record in data
        new_values = {}
        success_flag = False  # Flag to indicate if any record meets the conditions

        for record in data:
            # Check if the color code matches
            if record.cc == existing_color_code:
                # Update new_values dictionary
                new_values.update({
                    'sku': record.sku,
                    'article_num': record.article,
                    'retail_usd': record.retail_usd,
                    'retail_cad': record.retail_cad,
                    'retail_gbp': record.retail_gbp,
                    'size_id': record.size
                })

                # Check if all specified fields are non-empty
                if record.sku and record.article:
                    success_flag = True

        if not success_flag:
            return None

        return new_values


    # RFID Posting
    xml_content = fields.Binary("XML Content", readonly=True)

    def action_post_rfid(self):
        customer_orders = {}

        for line in self.line_ids:
            if line.POwithLine not in customer_orders:
                customer_orders[line.POwithLine] = {
                    "details": {
                        "itlcode": "3",
                        "chainid": line.ChainID_id,
                        "ocscustno": line.CustomerID,
                        "delivery_address_id": line.AddressID,
                        "delivery_contact": line.consignee_name,  # need to pass actual customer
                        "delivery_method": "TRUCK",
                        "delivery_account_no": "ITL",
                    },
                    "orders": {},
                    # "sizes": [],
                }

            # existing_orders = [
            #     order["product_ref"]
            #     for order in customer_orders[line.POwithLine]["orders"]
            # ]
            # if line.ProductRef not in existing_orders:
            if line.ProductRef not in customer_orders[line.POwithLine]["orders"]:
                customer_orders[line.POwithLine]["orders"][line.ProductRef] = {
                    "details": {
                        "product_ref": line.ProductRef,
                        "vs_po_number": line.po_number,
                        "so_number": line.SoRefLv,
                        "po_date": line.po_date,
                        "line_item": line.purchase_order_item,
                        "item_code": line.material_code,
                        "vsd_style_6": "12345",
                        "order_quantity": line.quantity1,  # need to change the field name
                        "season": line.season,
                        "size_range": line.size_range,
                        "country_of_origin": "Made in Sri Lanka",
                    },
                    "sizes": [],
                }

            customer_orders[line.POwithLine]["orders"][line.ProductRef]["sizes"].append(
                {
                    "size": line.grid_value,
                    "size_id": line.size_id,
                    "po_number": line.po_number,
                    "style": line.customer_style,
                    "colour_code": line.color_code_2,
                    "sku": line.sku,
                    "article_number": line.article_num,
                    "delivery_date": line.delivery_date,
                    "retail_price": line.retail_usd,
                    "retail_price2": line.retail_cad,
                    "retail_price3": line.retail_gbp,
                    "size_quantity": line.quantity,
                }
            )
        root = ET.Element("customerorders")

        for POwithLine, order_data in customer_orders.items():
            current_customer_order = ET.SubElement(root, "customerorder")

            customer_order_no = ET.SubElement(
                current_customer_order, "customer_order_no"
            )
            customer_order_no.text = POwithLine

            details = order_data["details"]
            for key, value in details.items():
                detail_elem = ET.SubElement(current_customer_order, key.lower())
                detail_elem.text = str(value)

            worksorders_elem = ET.SubElement(current_customer_order, "worksorders")

            for product_ref, order in order_data["orders"].items():
                current_works_order = ET.SubElement(worksorders_elem, "worksorder")

                product_ref_element = ET.SubElement(current_works_order, "product_ref")
                product_ref_element.text = order["details"]["product_ref"]

                vspo_element = ET.SubElement(current_works_order, "vs_po_number")
                vspo_element.text = order["details"]["vs_po_number"]

                so_no_elem1 = ET.SubElement(current_works_order, "so_number")
                so_no_elem1.text = order["details"]["so_number"]

                po_date_element = ET.SubElement(current_works_order, "po_date")
                po_date_element.text = order["details"]["po_date"].strftime("%Y-%m-%d")

                line_item_ele = ET.SubElement(current_works_order, "line_item")
                line_item_ele.text = order["details"]["line_item"]

                item_code_ele = ET.SubElement(current_works_order, "item_code")
                item_code_ele.text = order["details"]["item_code"]

                vsd_style_6_ele = ET.SubElement(current_works_order, "vsd_style_6")
                vsd_style_6_ele.text = order["details"]["vsd_style_6"]  # check

                order_quantity_ele = ET.SubElement(
                    current_works_order, "order_quantity"
                )
                # order_quantity_ele.text = order["order_quantity"]
                order_quantity_ele.text = str(order["details"]["order_quantity"])

                season_ele = SubElement(current_works_order, "season")
                season_ele.text = order["details"]["season"]

                size_range_ele = SubElement(current_works_order, "size_range")
                size_range_ele.text = order["details"]["size_range"]

                country_of_origin_ele = SubElement(
                    current_works_order, "country_of_origin"
                )
                country_of_origin_ele.text = order["details"]["country_of_origin"]

                sizelines_elem = ET.SubElement(current_works_order, "sizelines")
                for size_data in order["sizes"]:
                    size_line_elem = ET.SubElement(sizelines_elem, "size_line")

                    size_column = "size_lv" if "size_lv" in size_data else "size"
                    size_elem = ET.SubElement(size_line_elem, "size")
                    size_elem.text = size_data[size_column]

                    size_id_elem = ET.SubElement(size_line_elem, "size_id")
                    size_id_elem.text = size_data["size_id"]

                    po_no_elem = ET.SubElement(size_line_elem, "po_number")
                    po_no_elem.text = size_data.get("po_number", "")

                    style_no_elem = ET.SubElement(size_line_elem, "style")
                    style_no_elem.text = size_data["style"]

                    colour_code_elem = ET.SubElement(size_line_elem, "colour_code")
                    colour_code_elem.text = size_data["colour_code"]

                    sku_elem = ET.SubElement(size_line_elem, "sku")
                    sku_elem.text = size_data["sku"]

                    article_elem = ET.SubElement(size_line_elem, "article_number")
                    article_elem.text = size_data["article_number"]

                    if size_data["delivery_date"]:
                        delivery_date = ET.SubElement(size_line_elem, "delivery_date")
                        delivery_date.text = size_data["delivery_date"].strftime(
                            "%Y-%m-%d"
                        )

                    retail_price_ele = ET.SubElement(size_line_elem, "retail_price")
                    retail_price_ele.text = (
                        "${:.2f}".format(float(size_data["retail_price"]))
                        if size_data["retail_price"]
                        else ""
                    )

                    retail_price2_ele = ET.SubElement(size_line_elem, "retail_price2")
                    retail_price2_ele.text = (
                        "${:.2f}".format(float(size_data["retail_price2"]))
                        if size_data["retail_price2"]
                        else ""
                    )

                    retail_price3_ele = ET.SubElement(size_line_elem, "retail_price3")
                    retail_price3_ele.text = size_data["retail_price3"]

                    sizeqty_elem = ET.SubElement(size_line_elem, "size_quantity")
                    # sizeqty_elem.text = size_data["size_quantity"]
                    sizeqty_elem.text = str(size_data["size_quantity"])

        # xml_str = tostring(root, encoding="utf-8").decode("utf-8")
        # raise UserError(_("Generated XML:\n%s") % xml_str)
        xml_data = ET.tostring(root)
        xml_str_rfid = xml_data.decode("utf-8")
        dom = minidom.parseString(xml_str_rfid)
        pretty_xml_str_rfid = dom.toprettyxml(indent="    ")

        soap_envelope_rfid = (
            "<?xml version='1.0' encoding='UTF-8'?>"
            '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">'
            "<soap:Header/>"
            "<soap:Body>"
            '<ser:xmlinput xmlns:ser="http://services.web.labelvantage.com"/>'
            '<ser:xmlinput xmlns:ser="http://services.web.labelvantage.com"/>'
            '<ser:xmlinput xmlns:ser="http://services.web.labelvantage.com"/>'
            '<ser:xmlinput xmlns:ser="http://services.web.labelvantage.com">'
            "<![CDATA[" + pretty_xml_str_rfid + "]]>"
            "</ser:xmlinput>"
            "</soap:Body>"
            "</soap:Envelope>"
        )

        # raise UserError(_("Generated XML:\n%s") % soap_envelope_rfid)

        wsdl_url = "http://labelvantage.itl-group.com:8080/lv_web/services/CustomerOrdersService?wsdl"
        # Create a session with HTTP basic authentication
        session = Session()
        session.auth = HTTPBasicAuth("brandixws", "brandixws01")
        client = Client(wsdl_url, transport=Transport(session=session))

        # Send the request
        response = client.service.createCustomerOrders(
            system="test",
            usercode="brandixws",
            userpass="brandixws01",
            xmlinput=pretty_xml_str_rfid,
        )

        # Print the response
        raise UserError(_("Response:\n%s") % response)

    xml_content = fields.Binary("XML Content", readonly=True)

    def action_check_rfid(self):
        customer_orders = {}

        for line in self.line_ids:
            if line.POwithLine not in customer_orders:
                customer_orders[line.POwithLine] = {
                    "details": {
                        "itlcode": "3",
                        "chainid": line.ChainID_id,
                        "ocscustno": line.CustomerID,
                        "delivery_address_id": line.AddressID,
                        "delivery_contact": line.consignee_name,  # need to pass actual customer
                        "delivery_method": "TRUCK",
                        "delivery_account_no": "ITL",
                    },
                    "orders": {},
                    # "sizes": [],
                }

            # existing_orders = [
            #     order["product_ref"]
            #     for order in customer_orders[line.POwithLine]["orders"]
            # ]
            # if line.ProductRef not in existing_orders:
            if line.ProductRef not in customer_orders[line.POwithLine]["orders"]:
                customer_orders[line.POwithLine]["orders"][line.ProductRef] = {
                    "details": {
                        "product_ref": line.ProductRef,
                        "vs_po_number": line.po_number,
                        "so_number": line.SoRefLv,
                        "po_date": line.po_date,
                        "line_item": line.purchase_order_item,
                        "item_code": line.material_code,
                        "vsd_style_6": "12345",
                        "order_quantity": line.quantity1,  # need to change the field name
                        "season": line.season,
                        "size_range": line.size_range,
                        "country_of_origin": "Made in Sri Lanka",
                    },
                    "sizes": [],
                }

            customer_orders[line.POwithLine]["orders"][line.ProductRef]["sizes"].append(
                {
                    "size": line.grid_value,
                    "size_id": line.size_id,
                    "po_number": line.po_number,
                    "style": line.customer_style,
                    "colour_code": line.color_code_2,
                    "sku": line.sku,
                    "article_number": line.article_num,
                    "delivery_date": line.delivery_date,
                    "retail_price": line.retail_usd,
                    "retail_price2": line.retail_cad,
                    "retail_price3": line.retail_gbp,
                    "size_quantity": line.quantity,
                }
            )
        root = ET.Element("customerorders")

        for POwithLine, order_data in customer_orders.items():
            current_customer_order = ET.SubElement(root, "customerorder")

            customer_order_no = ET.SubElement(
                current_customer_order, "customer_order_no"
            )
            customer_order_no.text = POwithLine

            details = order_data["details"]
            for key, value in details.items():
                detail_elem = ET.SubElement(current_customer_order, key.lower())
                detail_elem.text = str(value)

            worksorders_elem = ET.SubElement(current_customer_order, "worksorders")

            for product_ref, order in order_data["orders"].items():
                current_works_order = ET.SubElement(worksorders_elem, "worksorder")

                product_ref_element = ET.SubElement(current_works_order, "product_ref")
                product_ref_element.text = order["details"]["product_ref"]

                vspo_element = ET.SubElement(current_works_order, "vs_po_number")
                vspo_element.text = order["details"]["vs_po_number"]

                so_no_elem1 = ET.SubElement(current_works_order, "so_number")
                so_no_elem1.text = order["details"]["so_number"]

                po_date_element = ET.SubElement(current_works_order, "po_date")
                po_date_element.text = order["details"]["po_date"].strftime("%Y-%m-%d")

                line_item_ele = ET.SubElement(current_works_order, "line_item")
                line_item_ele.text = order["details"]["line_item"]

                item_code_ele = ET.SubElement(current_works_order, "item_code")
                item_code_ele.text = order["details"]["item_code"]

                vsd_style_6_ele = ET.SubElement(current_works_order, "vsd_style_6")
                vsd_style_6_ele.text = order["details"]["vsd_style_6"]  # check

                order_quantity_ele = ET.SubElement(
                    current_works_order, "order_quantity"
                )
                # order_quantity_ele.text = order["order_quantity"]
                order_quantity_ele.text = str(order["details"]["order_quantity"])

                season_ele = SubElement(current_works_order, "season")
                season_ele.text = order["details"]["season"]

                size_range_ele = SubElement(current_works_order, "size_range")
                size_range_ele.text = order["details"]["size_range"]

                country_of_origin_ele = SubElement(
                    current_works_order, "country_of_origin"
                )
                country_of_origin_ele.text = order["details"]["country_of_origin"]

                sizelines_elem = ET.SubElement(current_works_order, "sizelines")
                for size_data in order["sizes"]:
                    size_line_elem = ET.SubElement(sizelines_elem, "size_line")

                    size_column = "size_lv" if "size_lv" in size_data else "size"
                    size_elem = ET.SubElement(size_line_elem, "size")
                    size_elem.text = size_data[size_column]

                    size_id_elem = ET.SubElement(size_line_elem, "size_id")
                    size_id_elem.text = size_data["size_id"]

                    po_no_elem = ET.SubElement(size_line_elem, "po_number")
                    po_no_elem.text = size_data.get("po_number", "")

                    style_no_elem = ET.SubElement(size_line_elem, "style")
                    style_no_elem.text = size_data["style"]

                    colour_code_elem = ET.SubElement(size_line_elem, "colour_code")
                    colour_code_elem.text = size_data["colour_code"]

                    sku_elem = ET.SubElement(size_line_elem, "sku")
                    sku_elem.text = size_data["sku"]

                    article_elem = ET.SubElement(size_line_elem, "article_number")
                    article_elem.text = size_data["article_number"]

                    if size_data["delivery_date"]:
                        delivery_date = ET.SubElement(size_line_elem, "delivery_date")
                        delivery_date.text = size_data["delivery_date"].strftime(
                            "%Y-%m-%d"
                        )

                    retail_price_ele = ET.SubElement(size_line_elem, "retail_price")
                    retail_price_ele.text = (
                        "${:.2f}".format(float(size_data["retail_price"]))
                        if size_data["retail_price"]
                        else ""
                    )

                    retail_price2_ele = ET.SubElement(size_line_elem, "retail_price2")
                    retail_price2_ele.text = (
                        "${:.2f}".format(float(size_data["retail_price2"]))
                        if size_data["retail_price2"]
                        else ""
                    )

                    retail_price3_ele = ET.SubElement(size_line_elem, "retail_price3")
                    retail_price3_ele.text = size_data["retail_price3"]

                    sizeqty_elem = ET.SubElement(size_line_elem, "size_quantity")
                    # sizeqty_elem.text = size_data["size_quantity"]
                    sizeqty_elem.text = str(size_data["size_quantity"])

        # xml_str = tostring(root, encoding="utf-8").decode("utf-8")
        # raise UserError(_("Generated XML:\n%s") % xml_str)
        xml_data = ET.tostring(root)
        xml_str_rfid = xml_data.decode("utf-8")
        dom = minidom.parseString(xml_str_rfid)
        pretty_xml_str_rfid = dom.toprettyxml(indent="    ")

        soap_envelope_rfid = (
            "<?xml version='1.0' encoding='UTF-8'?>"
            '<soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">'
            "<soap:Header/>"
            "<soap:Body>"
            '<ser:xmlinput xmlns:ser="http://services.web.labelvantage.com"/>'
            '<ser:xmlinput xmlns:ser="http://services.web.labelvantage.com"/>'
            '<ser:xmlinput xmlns:ser="http://services.web.labelvantage.com"/>'
            '<ser:xmlinput xmlns:ser="http://services.web.labelvantage.com">'
            "<![CDATA[" + pretty_xml_str_rfid + "]]>"
            "</ser:xmlinput>"
            "</soap:Body>"
            "</soap:Envelope>"
        )

        raise UserError(_("Generated XML:\n%s") % soap_envelope_rfid)