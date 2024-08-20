import requests
import base64
from io import BytesIO
import xlrd
from xml.etree import ElementTree as ET
from odoo import models, fields, api, _
from odoo.exceptions import UserError, ValidationError
import zeep
from zeep import Client
from zeep.transports import Transport
from requests.auth import HTTPBasicAuth
from requests import Session
from xml.etree.ElementTree import Element, SubElement, tostring
import xml.etree.ElementTree as ET
from xml.dom import minidom
from lxml import etree
from collections import defaultdict
from datetime import date, timedelta
import xmlrpc.client


class GetPo(models.Model):
    _name = "get_po_mas"
    _description = "Purchase Order"
    _rec_name = "order_number"

    order_number = fields.Char(string="Order Number", required=True)
    show_xml_response = fields.Selection(
        [("True", "Yes"), ("False", "No")],
        string="Show XML",
        default="False",
        store=True,
    )
    xml_response = fields.Text(string="XML", readonly=False)

    current_user = fields.Char(string="Current User", compute="_compute_current_user")
    current_user_img = fields.Image(string="Current User Image", compute="_compute_current_user_img")

    def _compute_current_user_img(self):
        for record in self:
            record.current_user_img = self.env.user.image_1920

    name = fields.Char(
        string="Order Ref",
        copy=False,
        default="New",
        index="trigram",
        compute="_order_ref",
    )
    state = fields.Selection(
        [
            ("New", "New"),
            ("Matched", "Matched"),
            ("Posted", "Posted"),
        ],
        string="Status",
        readonly=True,
        index=True,
        copy=False,
        default="New",
        tracking=True,
    )
    priority = fields.Selection(
        [("0", "Normal"), ("1", "Urgent")], "Priority", default="0", index=True
    )

    @api.depends("order_number", "ChoosePo")
    def _order_ref(self):
        for record in self:
            if record.order_number and record.ChoosePo:
                record.name = f"{record.ChoosePo}/{record.order_number}"
            else:
                record.name = False

    def _compute_current_user(self):
        for record in self:
            record.current_user = self.env.user.name

    line_ids = fields.One2many("get_po_mas_lines", "header_table", string="Order Lines")
    line_ids_main_lable = fields.One2many(
        "get_po_mas_lines_main_lable", "header_table", string="Order Lines Main Lable"
    )
    line_ids_care_lable = fields.One2many(
        "get_po_mas_lines_care_lable", "header_table", string="Order Lines Care Lable"
    )
    line_ids_price_tkt = fields.One2many(
        "get_po_mas_lines_price_tkt", "header_table", string="Order Lines Price tkt"
    )

    pdm = fields.Selection(
        [("PDM300", "PDM300"), ("PSI100", "PSI100")],
        string="System",
        default="PDM300",
        required=True,
    )
    ChoosePo = fields.Selection(
        [
            ("None", "None"),
            ("RFID", "RFID"),
            ("CARE LABELS", "CARE LABELS"),
            ("PRICE TKT / BARCODE STK", "PRICE TKT / BARCODE STK"),
            ("MAIN LABELS", "MAIN LABELS"),
        ],
        string="Choose Po",
        default="RFID",
        required=True,
    )
    DelDate = fields.Date(string="Delivery Date")
    vsd = fields.Char(string="Vsd")
    vendor_id = fields.Char(string="Vendor Id")
    Status = fields.Selection(
        [
            ("Success", "Success"),
            ("Open", "Open"),
            ("Cancelled", "Cancelled"),
            ("Progress", "Progress"),
        ],
        string="Status",
        default="Open",
    )
    RnNumber = fields.Selection(
        [("54867", "54867")], string="Rn Number", default="54867"
    )
    CaNumber = fields.Selection(
        [("67359", "67359")], string="Ca number", default="67359"
    )
    ChainID = fields.Many2one("chain_master", string="Chain Id", store=True)
    ChainID_id = fields.Char(string="Chain Id", compute="_compute_chain_id", store=True)
    matching_status = fields.Selection(
        [
            ("Success", "Success"),
            ("Fail", "Fail"),
            ("Not Matched Yet", "Not Matched Yet"),
        ],
        string="Match Status",
        default="Not Matched Yet",
    )

    additional_care_instruction = fields.Many2one(
        "additional_care_instruction", string="Additional Care Instruction"
    )
    additional_care_instruction_name = fields.Char(
        string="Additional Care Instruction",
        compute="_compute_additional_care_instruction_name",
        store=True,
    )

    @api.depends("additional_care_instruction")
    def _compute_additional_care_instruction_name(self):
        for record in self:
            if record.additional_care_instruction:
                record.additional_care_instruction_name = (
                    record.additional_care_instruction.additional_care_instruction_name
                )
            else:
                record.additional_care_instruction_name = False

    # @api.model
    # def compute_total_orders(self):
    #     total_purchase_orders = {
    #         'all_total_order': len(self.search([])),
    #         'success': len(self.search([("Status", "=", "Success")])),
    #     }
    #     return total_purchase_orders

    @api.model
    def get_purchase_order_count(self):
        today = date.today()

        # Get the counts for each status
        total_orders = len(self.env["get_po_mas"].search([]))
        done_count = len(self.env["get_po_mas"].search([("Status", "=", "Success")]))
        cancelled_count = len(self.env["get_po_mas"].search([("Status", "=", "Cancelled")]))
        open_count = len(self.env["get_po_mas"].search([("Status", "=", "Open")]))
        rfid_count = len(self.env["get_po_mas"].search([("ChoosePo", "=", "RFID")]))
        main_count = len(self.env["get_po_mas"].search([("ChoosePo", "=", "MAIN LABELS")]))
        care_count = len(self.env["get_po_mas"].search([("ChoosePo", "=", "CARE LABELS")]))
        price_tkt_count = len(self.env["get_po_mas"].search([("ChoosePo", "=", "PRICE TKT / BARCODE STK")]))

        # Calculate percentages
        def calculate_percentage(count, total):
            return (count / total * 100) if total > 0 else 0

        purchase_order_count = {
            "all_purchase_order": total_orders,
            "done": done_count,
            "cancelled": cancelled_count,
            "open": open_count,
            "done_percentage": calculate_percentage(done_count, total_orders),
            "cancelled_percentage": calculate_percentage(cancelled_count, total_orders),
            "open_percentage": calculate_percentage(open_count, total_orders),
            "rfid_count": rfid_count,
            "care_labels_count": care_count,
            "main_label_count": main_count,  # Fixed typo from 'main_lable_count'
            "price_tkt_count": price_tkt_count,
            "today_order_count": len(
                self.env["get_po_mas"].search([
                    ("create_date", ">=", today),
                    ("create_date", "<", today + timedelta(days=1))
                ])
            ),
            "rfid_percentage": calculate_percentage(rfid_count, total_orders),
            "care_percentage": calculate_percentage(care_count, total_orders),
            "main_percentage": calculate_percentage(main_count, total_orders),
            "price_tkt_percentage": calculate_percentage(price_tkt_count, total_orders),
            "current_user_img": self.env.user.image_1920,
            "current_user": self.env.user.name
        }

        return purchase_order_count

    @api.depends("ChainID")
    def _compute_chain_id(self):
        for record in self:
            if record.ChainID:
                record.ChainID_id = record.ChainID.ChainId
            else:
                record.ChainID_id = False

    ChainID_id_name = fields.Char(
        string="Chain Id Name", compute="_compute_chain_id_name", store=True
    )

    @api.depends("ChainID")
    def _compute_chain_id_name(self):
        for record in self:
            if record.ChainID:
                record.ChainID_id_name = record.ChainID.ChainName
            else:
                record.ChainID_id_name = False

    color_desc = fields.Char(string="Color Desc")
    style_number = fields.Char(string="Style Number")
    FactoryID = fields.Char(string="Factory Id")

    ProductRef = fields.Many2one("product_reference_master", string="Product Ref")
    ProductRef_name = fields.Char(
        string="Product Ref", compute="_compute_PRODUCT_REF_name"
    )

    @api.depends("ProductRef")
    def _compute_PRODUCT_REF_name(self):
        for record in self:
            if record.ProductRef:
                record.ProductRef_name = record.ProductRef.ProductRef_name
            else:
                record.ProductRef_name = False

    Collection = fields.Many2one("collection_master", string="Collection")
    Collection_name = fields.Char(string="Collection", compute="_compute_collection")

    @api.depends("Collection")
    def _compute_collection(self):
        for record in self:
            if record.Collection:
                record.Collection_name = record.Collection.Collection_name
            else:
                record.Collection_name = False

    silhouette = fields.Many2one("silhouette_master", string="Silhouette")
    silhouette_name = fields.Char(string="Silhouette", compute="_compute_silhouette")

    @api.depends("silhouette")
    def _compute_silhouette(self):
        for record in self:
            if record.silhouette:
                record.silhouette_name = record.silhouette.silhouette_name
            else:
                record.silhouette_name = False

    ItlCode = fields.Many2one("itl_code", string="ItlCode")
    ItlCode_name = fields.Char(string="ItlCode", compute="_compute_ItlCode")

    @api.depends("ItlCode")
    def _compute_ItlCode(self):
        for record in self:
            if record.ItlCode:
                record.ItlCode_name = record.ItlCode.ItlCode_Name
            else:
                record.ItlCode_name = False

    """Coo Details"""
    Coo = fields.Many2one("coo_master", string="Coo")
    Coo_name = fields.Char(string="Coo", compute="_compute_coo")

    @api.depends("Coo")
    def _compute_coo(self):
        for record in self:
            if record.Coo:
                record.Coo_name = record.Coo.coo_name
            else:
                record.Coo_name = False

    """Season Details"""
    season = fields.Many2one("seson_master", string="Season")
    season_name = fields.Char(string="Season", compute="_compute_season_name")

    @api.depends("season")
    def _compute_season_name(self):
        for record in self:
            if record.season:
                record.season_name = record.season.season_name
            else:
                record.season_name = False
    

    '''combo color code'''
    combo_color_code = fields.Many2one("combo_color_code_master", string="Combo Color Code", store=True)
    combo_color_code_name = fields.Char(
        string="Combo Color Code Name", compute="_compute_combo_color_code"
    )

    @api.depends("combo_color_code")
    def _compute_combo_color_code(self):
        for record in self:
            if record.combo_color_code:
                record.combo_color_code_name = record.combo_color_code.combo_color_code_name
            else:
                record.combo_color_code_name = False

    """Customer Details and Delivery address Details"""
    Customer = fields.Many2one("res.partner", string="Customer", store=True)
    Customer_name = fields.Char(
        string="Customer Name", compute="_compute_customer_name"
    )

    @api.depends("Customer")
    def _compute_customer_name(self):
        for record in self:
            if record.Customer:
                record.Customer_name = record.Customer.name
            else:
                record.Customer_name = False

    DeliveryAddress = fields.Many2one(
        "res.partner",
        string="Delivery Address",
        domain="[('parent_id', '=', Customer), ('type', '=', 'delivery')]",
    )

    @api.onchange("Customer")
    def onchange_customer(self):
        if self.Customer:
            # Set DeliveryAddress domain to show only addresses related to the selected customer
            return {
                "domain": {"DeliveryAddress": [("id", "child_of", self.Customer.id)]}
            }
        else:
            return {"domain": {"DeliveryAddress": []}}

    DeliveryAddressId = fields.Char(
        string="Delivery Address Id", compute="_compute_d_add_id", store=True
    )

    @api.depends("DeliveryAddress")
    def _compute_d_add_id(self):
        for record in self:
            if record.DeliveryAddress:
                record.DeliveryAddressId = record.DeliveryAddress.phone
            else:
                record.DeliveryAddressId = False

    AddressID = fields.Char(string="Address Id", compute="_compute_a_id", store=True)

    @api.depends("Customer")
    def _compute_a_id(self):
        for record in self:
            if record.Customer:
                record.AddressID = record.Customer.mobile
            else:
                record.AddressID = False

    CustomerID = fields.Char(string="Customer Id", compute="_compute_c_id", store=True)

    @api.depends("Customer")
    def _compute_c_id(self):
        for record in self:
            if record.Customer:
                record.CustomerID = record.Customer.vat
            else:
                record.CustomerID = False

    """Date of Manu"""
    date_of_manufacture = fields.Date(string="Date Manufacture")

    @api.depends("date_of_manufactur")
    def _compute_last_four_letters(self):
        for record in self:
            if record.Dateofmanu:
                month = str(record.Dateofmanu.month).zfill(
                    2
                )  # Ensure two digits for the day
                year = str(record.Dateofmanu.year)[
                    -2:
                ]  # Extract last two digits of the year
                record.date = month + " " + year
            else:
                record.date = ""

    """Size Data"""
    size_range = fields.Many2one("size_range_master", string="Size Range")
    Size_Range_name = fields.Char(
        string="Size Range", compute="_compute_size_range_name", store=True
    )

    @api.depends("size_range")
    def _compute_size_range_name(self):
        for record in self:
            if record.size_range:
                record.Size_Range_name = record.size_range.Size_Range_name
            else:
                record.Size_Range_name = ""

    """Care Instructions"""
    additional_ins = fields.Many2one(
        "additional_instruction_master", string="Additional Instruction"
    )
    additional_ins_name = fields.Char(
        string="Additional Instruction", compute="_compute_additional_ins"
    )

    @api.depends("additional_ins")
    def _compute_additional_ins(self):
        for record in self:
            if record.additional_ins:
                record.additional_ins_name = record.additional_ins.additional_ins_name
            else:
                record.additional_ins_name = False

    care_instruction_set_code = fields.Many2one(
        "care_instruction_set_code_master", string="Care Intruction Set Code"
    )
    care_instruction_set_code_2 = fields.Char(
        string="Care Intruction Set Code",
        compute="_compute_care_instruction_set_code_2",
    )

    @api.depends("care_instruction_set_code")
    def _compute_care_instruction_set_code_2(self):
        for record in self:
            if record.care_instruction_set_code:
                record.care_instruction_set_code_2 = (
                    record.care_instruction_set_code.care_instruction_set_code_2
                )
            else:
                record.care_instruction_set_code_2 = False

    """Get Po Details"""

    def fetch_po_data(self):
        if self.line_ids:
            raise UserError(_("Data already fetched. Cannot perform operation again."))

        if self.line_ids_care_lable:
            raise UserError(_("Data already fetched. Cannot perform operation again."))

        if self.line_ids_main_lable:
            raise UserError(_("Data already fetched. Cannot perform operation again."))

        if self.line_ids_price_tkt:
            raise UserError(_("Data already fetched. Cannot perform operation again."))

        url = "https://nwportal.masholdings.com/POXMLDownload/Config1?wsdl"
        headers = {"Content-Type": "text/xml"}

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
            response_xml = response.content.decode("utf-8")

            try:
                root = ET.fromstring(response_xml)
                encoded_data_tag = root.find(".//return")

                if encoded_data_tag is not None:
                    encoded_data = encoded_data_tag.text
                    decoded_data = base64.b64decode(encoded_data)
                    decoded_xml_string = decoded_data.decode("utf-8")
                    decoded_root = ET.fromstring(decoded_xml_string)

                    if not decoded_root.findall(".//PurchaseOrder"):
                        raise UserError(
                            f"No Purchase Order found for the given number: {self.order_number}"
                        )

                    # Clear existing lines based on the selected 'ChoosePo'
                    if self.ChoosePo == "RFID":
                        self.line_ids.unlink()
                        model_to_create = "get_po_mas_lines"
                    elif self.ChoosePo == "CARE LABELS":
                        self.line_ids_care_lable.unlink()
                        model_to_create = "get_po_mas_lines_care_lable"
                    elif self.ChoosePo == "MAIN LABELS":
                        self.line_ids_main_lable.unlink()
                        model_to_create = "get_po_mas_lines_main_lable"
                    elif self.ChoosePo == "PRICE TKT / BARCODE STK":
                        self.line_ids_price_tkt.unlink()
                        model_to_create = "get_po_mas_lines_price_tkt"
                    else:
                        raise UserError("Invalid selection for ChoosePo")

                    lines_to_create = []

                    def valid_date(date_str):
                        try:
                            if date_str and date_str != "0000-00-00":
                                return date_str
                        except ValueError:
                            pass
                        return None

                    for order in decoded_root.findall(".//PurchaseOrder"):
                        order_values = {
                            "header_table": self.id,
                            "po_number": order.findtext(
                                "PurchaseOrderNumber", default=""
                            ),
                            "purchase_order_version": order.findtext(
                                "PurchaseOrderVersion", default=""
                            ),
                            "po_date": valid_date(
                                order.findtext("PurchaseOrderDate", default="")
                            ),
                            "consignee_name": order.findtext(
                                "ConsigneeName", default=""
                            ),
                            "consignee_name2": order.findtext(
                                "ConsigneeName2", default=""
                            ),
                            "consignee_name3": order.findtext(
                                "ConsigneeName3", default=""
                            ),
                            "consignee_add1": order.findtext(
                                "ConsigneeAdd1", default=""
                            ),
                            "consignee_add2": order.findtext(
                                "ConsigneeAdd2", default=""
                            ),
                            "contact_person": order.findtext(
                                "ContactPerson", default=""
                            ),
                            "contact_tel": order.findtext("ContactTel", default=""),
                            "contact_email": order.findtext("ContactEMail", default=""),
                            "supplier_name": order.findtext("SupplierName", default=""),
                            "supplier_add1": order.findtext("SupplierAdd1", default=""),
                            "supplier_add2": order.findtext("SupplierAdd2", default=""),
                            "supplier_tel": order.findtext("SupplierTel", default=""),
                            "supplier_fax": order.findtext("SupplierFax", default=""),
                            "bill_to_name": order.findtext("BillToName", default=""),
                            "bill_to_name2": order.findtext("BillToName2", default=""),
                            "bill_to_name3": order.findtext("BillToName3", default=""),
                            "bill_to_add1": order.findtext("BillToAdd1", default=""),
                            "bill_to_add2": order.findtext("BillToAdd2", default=""),
                            "notify_add1": order.findtext("NotifyAdd1", default=""),
                            "notify_add2": order.findtext("NotifyAdd2", default=""),
                            "season": order.findtext("Season", default=""),
                            "cus_field1": order.findtext("CusField1", default=""),
                            "end_buyer_account": order.findtext(
                                "EndBuyerAccnt", default=""
                            ),
                            "end_buyer": order.findtext("EndBuyer", default=""),
                            "inco_terms": order.findtext("IncoTerms", default=""),
                            "inco_term_desc": order.findtext(
                                "IncoTermDesc", default=""
                            ),
                            "payment_mode": order.findtext("PaymentMode", default=""),
                            "delivery_address_code": order.findtext(
                                "DeliveryAddressCode", default=""
                            ),
                            "delivery_address": order.findtext(
                                "DeliveryAddress", default=""
                            ),
                            "header_text": order.findtext("HeaderText", default=""),
                            "header_note": order.findtext("HeaderNote", default=""),
                            "order_mode": order.findtext("OrderMode", default=""),
                            "company_code": order.findtext("CompanyCode", default=""),
                            "initial_release_date": valid_date(
                                order.findtext("InitialReleaseDate", default="")
                            ),
                            "initial_release_time": order.findtext(
                                "InitialReleaseTime", default=""
                            ),
                            "final_release_date": valid_date(
                                order.findtext("FinalReleaseDate", default="")
                            ),
                        }

                        line_items = order.find("LineItems").findall("LineItem")
                        for line_item in line_items:
                            customer_style = line_item.findtext(
                                "CustomerStyle", default=""
                            )
                            line_values = {
                                **order_values,
                                "purchase_order_item": line_item.findtext(
                                    "PurchaseOrderItem", default=""
                                ),
                                "material_code": line_item.findtext(
                                    "MaterialCode", default=""
                                ),
                                "vendor_material": line_item.findtext(
                                    "VendorMaterial", default=""
                                ),
                                "color_code": line_item.findtext(
                                    "ColorCode", default=""
                                ),
                                "color_code_2": line_item.findtext(
                                    "FinishedGoodColorCode", default=""
                                ),
                                "ref_material": line_item.findtext(
                                    "RefMaterial", default=""
                                ),
                                "ref_material_2": line_item.findtext(
                                    "RefMaterial2", default=""
                                ),
                                "item_text": line_item.findtext("ItemText", default=""),
                                "mat_po_text": line_item.findtext(
                                    "MatPoText", default=""
                                ),
                                "page_format": line_item.findtext(
                                    "PageFormat", default=""
                                ),
                                "material_description": line_item.findtext(
                                    "MaterialDescription", default=""
                                ),
                                "sales_order_line": line_item.findtext(
                                    "SalesOrder", default=""
                                ),
                                "sales_order_item": line_item.findtext(
                                    "SalesOrderItem", default=""
                                ),
                                "delivery_date": valid_date(
                                    line_item.findtext("DeliveryDate", default="")
                                ),
                                "order_quantity": float(
                                    line_item.findtext("Quantity", "0").strip() or 0
                                ),
                                "uom": line_item.findtext("UOM", default=""),
                                "net_price": float(
                                    line_item.findtext("NetPrice", "0").strip() or 0
                                ),
                                "net_value": float(
                                    line_item.findtext("NetValue", "0").strip() or 0
                                ),
                                "per": line_item.findtext("Per", default=""),
                                "discount_percentage": float(
                                    line_item.findtext(
                                        "DiscountPercentage", "0"
                                    ).strip()
                                    or 0
                                ),
                                "discount_value": float(
                                    line_item.findtext("DiscountValue", "0").strip()
                                    or 0
                                ),
                                "text": line_item.findtext("Text", default=""),
                                "product_type": line_item.findtext(
                                    "ProductType", default=""
                                ),
                                "gender": line_item.findtext("Gender", default=""),
                                "order_reason": line_item.findtext(
                                    "OrderReason", default=""
                                ),
                                "garment_type": line_item.findtext(
                                    "GarmentType", default=""
                                ),
                                "ptlcode": line_item.findtext("PTLcode", default=""),
                                "ship_mode": line_item.findtext("ShipMode", default=""),
                                "sales_order_season": line_item.findtext(
                                    "SalesOrderSeason", default=""
                                ),
                                "buy_year": line_item.findtext("BuyYear", default=""),
                                "brand": line_item.findtext("Brand", default=""),
                                "department_code": line_item.findtext(
                                    "DepartmentCode", default=""
                                ),
                                "emotional_space": line_item.findtext(
                                    "EmotionalSpace", default=""
                                ),
                                "planning_group": line_item.findtext(
                                    "PlanningGroup", default=""
                                ),
                                "cpo": line_item.findtext("CPO", default=""),
                                "ex_factory_date": valid_date(
                                    line_item.findtext("ExFactoryDate", default="")
                                ),
                                "customer_style": line_item.findtext(
                                    "CustomerStyle", default=""
                                ),
                                "customer_style_desc": line_item.findtext(
                                    "CustomerStyleDesc", default=""
                                ),
                                "customer_ref1": line_item.findtext(
                                    "CustomerRef1", default=""
                                ),
                            }

                            if len(customer_style) == 8:
                                line_values["vss_no"] = customer_style
                                line_values["customer_style"] = customer_style
                            else:
                                line_values["vsd_style_6"] = customer_style
                                line_values["vsd_style_9"] = customer_style

                            schedule_lines = line_item.find("ScheduleLines").findall(
                                "ScheduleLine"
                            )
                            for schedule_line in schedule_lines:
                                schedule_line_values = {
                                    "schedule_line_no": schedule_line.findtext(
                                        "ScheduleLineNo", default=""
                                    ),
                                    "grid_value": schedule_line.findtext(
                                        "GridValue", default=""
                                    ),
                                    "delivery_date1": valid_date(
                                        schedule_line.findtext(
                                            "DeliveryDate", default=""
                                        )
                                    ),
                                    "sales_order_schedule_line": schedule_line.findtext(
                                        "SalesOrder", default=""
                                    ),
                                    "over_delivery_tolerance": float(
                                        schedule_line.findtext(
                                            "OverDeliveryTolerance", "0"
                                        ).strip()
                                        or 0
                                    ),
                                    "under_delivery_tolerance": float(
                                        schedule_line.findtext(
                                            "UnderDeliveryTolerance", "0"
                                        ).strip()
                                        or 0
                                    ),
                                    "size_quantity": float(
                                        schedule_line.findtext("Quantity", "0").strip()
                                        or 0
                                    ),
                                    "net_price": float(
                                        schedule_line.findtext("NetPrice", "0").strip()
                                        or 0
                                    ),
                                    "net_value": float(
                                        schedule_line.findtext("NetValue", "0").strip()
                                        or 0
                                    ),
                                    "vendor_material_code": schedule_line.findtext(
                                        "VendorMaterialCode", default=""
                                    ),
                                    "ex_factory_date": valid_date(
                                        schedule_line.findtext(
                                            "ExFactoryDate", default=""
                                        )
                                    ),
                                    "additional_sku_no": schedule_line.findtext(
                                        "AdditionalSKUNo", default=""
                                    ),
                                    "fg_size": schedule_line.findtext(
                                        "FGSize", default=""
                                    ),
                                    "additional_field_1": schedule_line.findtext(
                                        "AdditionalField1", default=""
                                    ),
                                    "additional_field_2": schedule_line.findtext(
                                        "AdditionalField2", default=""
                                    ),
                                }

                                final_values = {**line_values, **schedule_line_values}
                                lines_to_create.append(final_values)

                    if lines_to_create:
                        self.env[model_to_create].create(lines_to_create)
                    message = _("RECEIVED SUCCESSFULLY.")
                    return {
                        "type": "ir.actions.client",
                        "tag": "display_notification",
                        "params": {
                            "message": message,
                            "type": "success",
                            "sticky": True,
                            "next": {
                                "type": "ir.actions.client",
                                "tag": "reload",
                            },
                        },
                    }
                    # return {
                    #     'effect': {
                    #         'fadeout': 'slow',
                    #         'message': 'Data fetched and stored successfully.',
                    #         'type': 'rainbow_man',
                    #     }
                    # }

                else:
                    raise UserError(
                        f"Failed to retrieve Purchase Order data for the given number: {self.order_number}"
                    )
            except ET.ParseError:
                raise UserError(f"{decoded_xml_string}")
        else:
            raise UserError(f"Error: {response.status_code}\n{response.reason}")

    def fetch_po_data_xml(self):
        url = "https://nwportal.masholdings.com/POXMLDownload/Config1?wsdl"
        headers = {"Content-Type": "text/xml"}

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
            response_xml = response.content.decode("utf-8")

            try:
                root = ET.fromstring(response_xml)
                encoded_data_tag = root.find(".//return")

                if encoded_data_tag is not None:
                    encoded_data = encoded_data_tag.text
                    decoded_data = base64.b64decode(encoded_data)
                    decoded_xml_string = decoded_data.decode("utf-8")
                    decoded_root = ET.fromstring(decoded_xml_string)

                    self.xml_response = decoded_xml_string
                else:
                    raise UserError("Failed to find the expected data in the response.")
            except ET.ParseError:
                raise UserError("Failed to parse the XML response.")

    # def delete_records_from_related_model(self):
    #     if not self.order_number:
    #         raise UserError(_('Please provide a PO Number for deleting records.'))

    #     # Assuming lbx_mi_gpo_d001 is the related model
    #     gpo_d001_model = self.env['get_po_mas_lines']

    #     # Find records based on PoNumber
    #     records_to_delete = gpo_d001_model.search([('po_number', '=', self.order_number)])

    #     if not records_to_delete:
    #         raise UserError(_('No records found with PO Number %s' % self.order_number))

    #     # Delete the records in the related model
    #     records_to_delete.unlink()

    #     # Check if any records were deleted
    #     if records_to_delete:
    #         # Notification for success
    #         message = _("PO deleted successfully.")
    #         return {
    #             'type': 'ir.actions.client',
    #             'tag': 'display_notification',
    #             'params': {
    #                 'message': message,
    #                 'type': 'danger',
    #                 'sticky': True,
    #                 'next': {
    #                     'type': 'ir.actions.client',
    #                     'tag': 'reload',
    #                 }
    #             }
    #         }
    #     else:
    #         # No records deleted, show a different message or do nothing
    #         return {'type': 'ir.actions.do_nothing'}

    def delete_records_from_related_model(self):
        if not self.order_number:
            raise UserError(_("Please provide a PO Number for deleting records."))

        # Choose the model based on the value of the ChoosePo field
        if self.ChoosePo == "RFID":
            related_model = self.env["get_po_mas_lines"]
            line_field = "line_ids"
        elif self.ChoosePo == "CARE LABELS":
            related_model = self.env["get_po_mas_lines_care_lable"]
            line_field = "line_ids_care_lable"
        elif self.ChoosePo == "PRICE TKT / BARCODE STK":
            related_model = self.env["get_po_mas_lines_price_tkt"]
            line_field = "line_ids_price_tkt"
        elif self.ChoosePo == "MAIN LABELS":
            related_model = self.env["get_po_mas_lines_main_lable"]
            line_field = "line_ids_main_lable"
        else:
            raise UserError(_("Invalid ChoosePo value."))

        # Find records based on PO Number
        records_to_delete = related_model.search(
            [("po_number", "=", self.order_number)]
        )

        if not records_to_delete:
            raise UserError(_("No records found with PO Number %s" % self.order_number))

        # Delete the records in the related model
        records_to_delete.unlink()

        # Check if any records were deleted
        if records_to_delete:
            # Notification for success
            message = _("PO deleted successfully.")
            return {
                "type": "ir.actions.client",
                "tag": "display_notification",
                "params": {
                    "message": message,
                    "type": "danger",
                    "sticky": True,
                    "next": {
                        "type": "ir.actions.client",
                        "tag": "reload",
                    },
                },
            }
        else:
            # No records deleted, show a different message or do nothing
            return {"type": "ir.actions.do_nothing"}

    selected_vpo_details = fields.Many2one("get_vpo_mas", string="Select Vpo")
    color_code_2 = fields.Char(string="Color Code 2", related="line_ids.color_code_2")

    # def compare_and_extract_data(self):
    #     if not self.line_ids:
    #         raise ValidationError(_('There Is No Data To Match'))

    #     if not self.selected_vpo_details:
    #         raise ValidationError(_('Please select the VPO details before comparing and extracting data.'))

    #     VPO = self.env['get_vpo_mas_lines']

    #     missing_records_details = []
    #     all_lines_success = True

    #     # Iterate through existing records and update values
    #     for existing_record in self.line_ids:
    #         # Find data based on matching criteria
    #         data = VPO.search([
    #             ('po_number', '=', existing_record.po_number),
    #             ('size_lv', '=', existing_record.grid_value),
    #             ('style', '=', existing_record.customer_style),
    #         ])

    #         new_values = self._extract_po_line_values(data, existing_record.color_code_2)

    #         if not self.color_code_2:
    #             raise ValidationError(_('Color Code Missing.'))

    #         if new_values:
    #             existing_record.write(dict(new_values))
    #         else:
    #             missing_records_details.append({
    #                 'line_number': existing_record.line_number,
    #                 'details': {
    #                     'PoNumber': existing_record.po_number,
    #                     'Size': existing_record.grid_value,
    #                     'Style': existing_record.customer_style,
    #                     'ColorCode': existing_record.color_code_2,
    #                 },
    #                 'reason': 'For This Po Records Matching criteria not found in VPO.',
    #             })
    #             all_lines_success = False
    #     # Update the matching status on the header record
    #     if all_lines_success:
    #         self.matching_status = 'Success'
    #     else:
    #         self.matching_status = 'Fail'

    #     if missing_records_details:
    #         error_message = "Data not transferred for the following line numbers:\n"
    #         for record_details in missing_records_details:
    #             error_message += (
    #                 f"Line Number: {record_details['line_number']}, "
    #                 f"Details: {record_details['details']}, "
    #                 f"Reason: {record_details['reason']}\n"
    #             )

    #         raise UserError(error_message)

    #     # Display success message and reload the view
    #     message = _("Data fetched and updated successfully.")
    #     return {
    #         'type': 'ir.actions.client',
    #         'tag': 'display_notification',
    #         'params': {
    #             'message': message,
    #             'type': 'success',
    #             'sticky': True,
    #             'next': {
    #                 'type': 'ir.actions.client',
    #                 'tag': 'reload',
    #             }
    #         }
    #     }

    def compare_and_extract_data(self):
        if (
            not self.line_ids
            and not self.line_ids_main_lable
            and not self.line_ids_care_lable
            and not self.line_ids_price_tkt
        ):
            raise ValidationError(_("There Is No Data To Match"))

        if not self.selected_vpo_details:
            raise ValidationError(
                _("Please select the VPO details before comparing and extracting data.")
            )

        VPO = self.env["get_vpo_mas_lines"]

        missing_records_details = []
        all_lines_success = True

        # Define the tables to iterate through
        line_tables = [
            ("line_ids", "get_po_mas_lines"),
            ("line_ids_main_lable", "get_po_mas_lines_main_lable"),
            ("line_ids_care_lable", "get_po_mas_lines_care_lable"),
            ("line_ids_price_tkt", "get_po_mas_lines_price_tkt"),
        ]

        # Iterate through each line table and perform the matching
        for line_table, model_name in line_tables:
            for existing_record in self[line_table]:
                # Find data based on matching criteria
                data = VPO.search(
                    [
                        ("po_number", "=", existing_record.po_number),
                        ("size_lv", "=", existing_record.grid_value),
                        ("style", "=", existing_record.customer_style),
                    ]
                )

                new_values = self._extract_po_line_values(
                    data, existing_record.color_code_2
                )

                if not existing_record.color_code_2:
                    raise ValidationError(_("Color Code Missing."))

                if new_values:
                    existing_record.write(dict(new_values))
                else:
                    missing_records_details.append(
                        {
                            "line_number": existing_record.line_number,
                            "details": {
                                "PoNumber": existing_record.po_number,
                                "Size": existing_record.grid_value,
                                "Style": existing_record.customer_style,
                                "ColorCode": existing_record.color_code_2,
                            },
                            "reason": f"For this PO, records matching criteria not found in {model_name}.",
                        }
                    )
                    all_lines_success = False

        # Update the matching status on the header record
        self.matching_status = "Success" if all_lines_success else "Fail"

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
            "type": "ir.actions.client",
            "tag": "display_notification",
            "params": {
                "message": message,
                "type": "success",
                "sticky": True,
                "next": {
                    "type": "ir.actions.client",
                    "tag": "reload",
                },
            },
        }

    def _extract_po_line_values(self, data, existing_color_code):
        # Extract and return values for each record in data
        new_values = {}
        success_flag = False  # Flag to indicate if any record meets the conditions

        for record in data:
            # Check if the color code matches
            if record.cc == existing_color_code:
                # Update new_values dictionary
                new_values.update(
                    {
                        "sku": record.sku,
                        "article_num": record.article,
                        "retail_usd": record.retail_usd,
                        "retail_cad": record.retail_cad,
                        "retail_gbp": record.retail_gbp,
                        "size_id": record.size,
                    }
                )

                # Check if all specified fields are non-empty
                if record.sku and record.article:
                    success_flag = True
                    self.update({"state": "Matched"})

        if not success_flag:
            return None

        return new_values

    # def _extract_po_line_values(self, data, existing_color_code):
    #     # Extract and return values for each record in data
    #     new_values = {}
    #     success_flag = False  # Flag to indicate if any record meets the conditions

    #     for record in data:
    #         # Check if the color code matches
    #         if record.cc == existing_color_code:
    #             # Update new_values dictionary
    #             new_values.update({
    #                 'sku': record.sku,
    #                 'article_num': record.article,
    #                 'retail_usd': record.retail_usd,
    #                 'retail_cad': record.retail_cad,
    #                 'retail_gbp': record.retail_gbp,
    #                 'size_id': record.size
    #             })

    #             # Check if all specified fields are non-empty
    #             if record.sku and record.article:
    #                 success_flag = True
    #                 self.update({'state': 'Matched'})

    #     if not success_flag:
    #         return None

    #     return new_values

    # ----------------------------------------------------------------------------------------------------------
    # RFID - Posting
    # ----------------------------------------------------------------------------------------------------------
    xml_content = fields.Binary("XML Content", readonly=True)

    def action_post_rfid(self):
        customer_orders = {}
        lines = self.env["get_po_mas_lines"].search([("header_table", "=", self.id)])

        # for line in self.line_ids:
        for line in lines:
            if line.POwithLine not in customer_orders:
                customer_orders[line.POwithLine] = {
                    "details": {
                        "itlcode": "3",
                        "chainid": line.ChainID_id,
                        "ocscustno": line.CustomerID,
                        "delivery_address_id": line.AddressID,
                        "delivery_contact": line.Customer_name,
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
                        "order_quantity": line.order_quantity,
                        "season": line.season,
                        "size_range": line.size_range,
                        "country_of_origin": line.Coo,
                    },
                    "sizes": [],
                }

            customer_orders[line.POwithLine]["orders"][line.ProductRef]["sizes"].append(
                {
                    "size": line.size_lv if line.size_lv else line.grid_value,
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
                    "size_quantity": line.size_quantity,
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

                    # size_column = "size_lv" if "size_lv" in size_data else "size"
                    size_elem = ET.SubElement(size_line_elem, "size")
                    size_elem.text = size_data["size"]  # check

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

        # request sending
        response = client.service.createCustomerOrders(
            system="test",
            usercode="brandixws",
            userpass="brandixws01",
            xmlinput=pretty_xml_str_rfid,
        )
        wizard = self.env["rfid.response.wizard"].create({"response_content": response})
        self._process_response(response)
        return {
            "type": "ir.actions.act_window",
            "res_model": "rfid.response.wizard",
            "view_mode": "form",
            "view_id": self.env.ref("ITL_LBX_MS_V2.view_rfid_response_wizard_form").id,
            "target": "new",
            "res_id": wizard.id,
        }

    def _process_response(self, response):
        # parsing the response
        root = ET.fromstring(response)

        # Iterate over each result
        for result in root.findall("result"):
            status = result.find("status").text
            customer_order_no = result.find("customer_order_no").text

            # Determine the new status
            if status == "error":
                new_status = "Open"
            elif status == "success":
                new_status = "Success"
            else:
                continue

            # Update the status in Odoo
            self._update_po_status(customer_order_no, new_status)

    def _update_po_status(self, customer_order_no, new_status):
        po_lines = self.env["get_po_mas_lines"].search(
            [("POwithLine", "=", customer_order_no)]
        )
        if po_lines:
            # Check if the current status is already 'Success'
            current_status = po_lines.mapped("StatusField")
            if "Success" in current_status:
                # If any line already has a status of 'Success', do not update it
                return
            po_lines.write({"StatusField": new_status})
        else:
            raise UserError(f"PO with line {customer_order_no} not found.")

    # ----------------------------------------------------------------------------------------------------------
    # RFID - XML
    # ----------------------------------------------------------------------------------------------------------
    xml_content = fields.Binary("XML Content", readonly=True)

    def action_check_rfid(self):
        customer_orders = {}
        lines = self.env["get_po_mas_lines"].search([("header_table", "=", self.id)])

        # for line in self.line_ids:
        for line in lines:
            if line.POwithLine not in customer_orders:
                customer_orders[line.POwithLine] = {
                    "details": {
                        "itlcode": "3",
                        "chainid": line.ChainID_id,
                        "ocscustno": line.CustomerID,
                        "delivery_address_id": line.AddressID,
                        "delivery_contact": line.Customer_name,
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
                        "order_quantity": line.order_quantity,
                        "season": line.season,
                        "size_range": line.size_range,
                        "country_of_origin": line.Coo,
                    },
                    "sizes": [],
                }

            customer_orders[line.POwithLine]["orders"][line.ProductRef]["sizes"].append(
                {
                    "size": line.size_lv if line.size_lv else line.grid_value,
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
                    "size_quantity": line.size_quantity,
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

                    # size_column = "size_lv" if "size_lv" in size_data else "size"
                    size_elem = ET.SubElement(size_line_elem, "size")
                    size_elem.text = size_data["size"]  # check

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

    # -----------------------------------------------------------------------------------------------------------
    # Main Label - Post
    # -----------------------------------------------------------------------------------------------------------

    def action_post_main(self):
        lines = self.env["get_po_mas_lines_main_lable"].search(
            [("header_table", "=", self.id)]
        )

        if not lines:
            raise UserError("No lines found for the given header.")

        ChainID_id = lines[0].ChainID_id if lines[0].ChainID_id else ""
        CustomerID = lines[0].CustomerID if lines[0].CustomerID else ""
        AddressID = lines[0].AddressID if lines[0].AddressID else ""
        Customer_name = lines[0].Customer_name if lines[0].Customer_name else ""
        po_number = lines[0].po_number if lines[0].po_number else ""
        # customer_style = lines[0].customer_style if lines[0].customer_style else ""
        # po_date = lines[0].po_date if lines[0].po_date else ""
        # style_number = lines[0].style_number if lines[0].style_number else ""
        # purchase_order_item = (
        #     lines[0].purchase_order_item if lines[0].purchase_order_item else ""
        # )
        # vendor_id = lines[0].vendor_id if lines[0].vendor_id else ""
        # FactoryID = lines[0].FactoryID if lines[0].FactoryID else ""
        # Group by POwithLine
        orders = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        so_ref_lvs = {}
        po_dates = {}
        style_nos = {}
        purchase_order_items = {}
        vendor_ids = {}
        date_of_manufacture_last_four_letters_all = {}
        Country = {}
        order_quantities = {}
        color_descr = {}
        vss_nos = {}
        vsd_style_6s = {}
        vsd_style_9s = {}
        RnNumbers = {}
        CaNumbers = {}
        for line in lines:
            POwithLine = line.POwithLine
            orders[line.POwithLine][
                line.ProductRef,
                line.season,
                line.material_code,
                line.FactoryID,
                line.silhouette,
                line.Collection,
                line.size_range,
            ][line.grid_value].append(line)
            if POwithLine not in so_ref_lvs:
                so_ref_lvs[POwithLine] = line.SoRefLv or ""
            if POwithLine not in po_dates:
                po_dates[POwithLine] = line.po_date or ""
            if POwithLine not in style_nos:
                style_nos[POwithLine] = line.style_number or ""
            if POwithLine not in purchase_order_items:
                purchase_order_items[POwithLine] = line.purchase_order_item or ""
            if POwithLine not in vendor_ids:
                vendor_ids[POwithLine] = line.vendor_id or ""
            if POwithLine not in date_of_manufacture_last_four_letters_all:
                date_of_manufacture_last_four_letters_all[POwithLine] = (
                    line.date_of_manufacture_last_four_letters or ""
                )
            if POwithLine not in Country:
                Country[POwithLine] = line.Coo or ""
            if POwithLine not in order_quantities:
                order_quantities[POwithLine] = line.order_quantity or ""

            if POwithLine not in color_descr:
                color_descr[POwithLine] = line.color_desc or ""

            if POwithLine not in vss_nos:
                vss_nos[POwithLine] = line.vss_no or ""

            if POwithLine not in vsd_style_6s:
                vsd_style_6s[POwithLine] = line.vsd_style_6 or ""

            if POwithLine not in vsd_style_9s:
                vsd_style_9s[POwithLine] = line.vsd_style_9 or ""

            if POwithLine not in RnNumbers:
                RnNumbers[POwithLine] = line.RnNumber or ""

            if POwithLine not in CaNumbers:
                CaNumbers[POwithLine] = line.CaNumber or ""
        # Start building the XML with formatting
        xml_body = "<customerorders>\n"

        for POwithLine, worksorders in orders.items():
            xml_body += "    <customerorder>\n"
            xml_body += f"        <itlcode>3</itlcode>\n"
            xml_body += f"         <chainid>{ChainID_id}</chainid>\n"
            xml_body += f"        <ocscustno>{CustomerID}</ocscustno>\n"
            xml_body += f"        <supplier_account></supplier_account>\n"
            xml_body += f"        <paying_party></paying_party>\n"
            xml_body += f"        <customer_order_no>{POwithLine}</customer_order_no>\n"
            xml_body += f"        <invoice_phone></invoice_phone>\n"
            xml_body += (
                f"        <delivery_address_id>{AddressID}</delivery_address_id>\n"
            )
            xml_body += (
                f"        <delivery_contact>{Customer_name}</delivery_contact>\n"
            )
            xml_body += f"        <delivery_method>TRUCK</delivery_method>\n"
            xml_body += f"        <delivery_account_no>ITL</delivery_account_no>\n"
            xml_body += (
                f"        <customer_confirmation_email></customer_confirmation_email>\n"
            )
            xml_body += f"        <comments></comments>\n"
            xml_body += f"        <quotation></quotation>\n"
            xml_body += "        <worksorders>\n"

            for (
                ProductRef,
                season,
                material_code,
                FactoryID,
                silhouette,
                Collection,
                size_range,
            ), sizelines in worksorders.items():
                xml_body += "            <worksorder>\n"
                xml_body += f"                <product_ref>{ProductRef}</product_ref>\n"
                xml_body += (
                    f"                <vs_po_number>{po_number}</vs_po_number>\n"
                )
                xml_body += (
                    f"                <po_date>{po_dates[POwithLine]}</po_date>\n"
                )
                xml_body += f"                <style_number>{style_nos[POwithLine]}</style_number>\n"
                xml_body += f"                <colour_descr>{color_descr[POwithLine]}</colour_descr>\n"
                xml_body += f"                <line_item>{purchase_order_items[POwithLine]}</line_item>\n"
                xml_body += (
                    f"                <so_number>{so_ref_lvs[POwithLine]}</so_number>\n"
                )
                xml_body += f"                <item_code>{material_code}</item_code>\n"
                xml_body += f"                <reg_no></reg_no>\n"
                xml_body += (
                    f"                <vendor_id>{vendor_ids[POwithLine]}</vendor_id>\n"
                )
                xml_body += f"                <style_descr></style_descr>\n"
                xml_body += f"                <factory_id>{FactoryID}</factory_id>\n"
                xml_body += f"                <itl_factory_code></itl_factory_code>\n"
                xml_body += f"                <silhouette>{silhouette}</silhouette>\n"
                xml_body += f"                <collection>{Collection}</collection>\n"
                xml_body += f"                <colour></colour>\n"  # need to discuss
                xml_body += f"                <vs_stores></vs_stores>\n"
                xml_body += f"                <vss_no>{vss_nos[POwithLine]}</vss_no>\n"
                xml_body += f"                <vsd_style_6>{vsd_style_6s[POwithLine]}</vsd_style_6>\n"
                xml_body += f"                <vsd_style_9>{vsd_style_9s[POwithLine]}</vsd_style_9>\n"
                xml_body += (
                    f"                <rn_number>{RnNumbers[POwithLine]}</rn_number>\n"
                )
                xml_body += (
                    f"                <ca_number>{CaNumbers[POwithLine]}</ca_number>\n"
                )
                xml_body += f"                <season>{season}</season>\n"
                xml_body += f"                <date_of_manuf>{date_of_manufacture_last_four_letters_all[POwithLine]}</date_of_manuf>\n"
                xml_body += f"                <country_of_origin>{Country[POwithLine]}</country_of_origin>\n"
                xml_body += f"                <order_quantity>{order_quantities[POwithLine]}</order_quantity>\n"
                xml_body += f"                <size_range>{size_range}</size_range>\n"
                xml_body += "                <sizelines>\n"

                for size, size_lines in sizelines.items():
                    xml_body += "                    <size_line>\n"
                    size_value = (
                        size_lines[0].size_lv if size_lines[0].size_lv else size
                    )
                    # xml_body += f"                        <size>{size}</size>\n"
                    xml_body += f"                        <size>{size_value}</size>\n"

                    # xml_body += f"                        <size_id>{size_lines[0].size_id}</size_id>\n"
                    xml_body += (
                        f"                        <po_number>{po_number}</po_number>\n"
                    )
                    customer_style = (
                        size_lines[0].customer_style
                        if size_lines[0].customer_style
                        else ""
                    )
                    xml_body += (
                        f"                        <style>{customer_style}</style>\n"
                    )
                    xml_body += f"                        <colour_code>{size_lines[0].color_code_2}</colour_code>\n"
                    xml_body += (
                        f"                        <panty_length></panty_length>\n"
                    )
                    xml_body += f"                        <desc>{size_lines[0].material_description}</desc>\n"
                    xml_body += f"                        <delivery_date>{size_lines[0].DelDate}</delivery_date>\n"
                    xml_body += f"                        <size_quantity>{size_lines[0].size_quantity}</size_quantity>\n"

                    xml_body += "                    </size_line>\n"

                xml_body += "                </sizelines>\n"
                # xml_body += "                <additional_instructions>\n"
                # for size, size_lines in sizelines.items():
                #     for line in size_lines:
                #         if line.additional_ins:
                #             # additional_instructions shoudl come bottom of the lines
                #             xml_body += f"                    <additional_instruction>{line.additional_ins}</additional_instruction>\n"

                # xml_body += "                </additional_instructions>\n"
                xml_body += "                <care_instruction_sets>\n"

                for size, size_lines in sizelines.items():
                    for line in size_lines:
                        if line.care_instruction_set_code:
                            xml_body += f"                    <care_instruction_set_code>{line.care_instruction_set_code}</care_instruction_set_code>\n"
                # xml_body += "                    <care_instruction_set_code></care_instruction_set_code>\n"
                xml_body += "                </care_instruction_sets>\n"
                xml_body += "                <additional_care_instructions>\n"
                for size, size_lines in sizelines.items():
                    for line in size_lines:
                        if line.additional_care_instruction:
                            # xml_body += f"                    <additional_care_instruction></additional_care_instruction>\n"
                            xml_body += f"                    <care_phrase>{line.additional_care_instruction}</care_phrase>\n"
                xml_body += "                </additional_care_instructions>\n"
                xml_body += "                <components>\n"
                try:
                    for size_line in size_lines:
                        composition = self.env["composition_master"].search(
                            [("id", "=", size_line.cid)], limit=1
                        )
                        if composition:
                            if composition.Component_1_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_1_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_1_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_1_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # except Exception as e:
                            # raise UserError(f"An error occurred: {str(e)}")
                            # Component2
                            if composition.Component_2_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_2_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_2_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_2_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"

                            # component 3

                            if composition.Component_3_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_3_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_3_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_3_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"

                            # component 4
                            if composition.Component_4_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_4_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_4_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_4_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"

                            # component 5
                            if composition.Component_5_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_5_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_5_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_5_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 6

                            if composition.Component_6_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_6_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_6_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_6_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"

                            # component 7

                            if composition.Component_7_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_7_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_7_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_7_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"

                            # component 8

                            if composition.Component_8_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_8_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_8_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_8_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"

                            # component 9

                            if composition.Component_9_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_9_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_9_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_9_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 10

                            if composition.Component_10_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_10_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_10_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_10_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                except Exception as e:
                    raise UserError(f"An error occurred: {str(e)}")

                xml_body += "                </components>\n"
                xml_body += "                <additional_instructions>\n"
                for size, size_lines in sizelines.items():
                    for line in size_lines:
                        if line.additional_ins:
                            # additional_instructions shoudl come bottom of the lines
                            xml_body += f"                    <additional_instruction>{line.additional_ins}</additional_instruction>\n"

                xml_body += "                </additional_instructions>\n"
                xml_body += "            </worksorder>\n"

            xml_body += "        </worksorders>\n"
            xml_body += "    </customerorder>\n"

        xml_body += "</customerorders>"

        # Complete XML structure with formatting
        xml_data = f"""<?xml version='1.0' encoding='UTF-8'?>
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
        <soap:Header />
        <soap:Body>
            <ser:xmlinput xmlns:ser="http://services.web.labelvantage.com">
                <![CDATA[
    {xml_body}
                ]]>
            </ser:xmlinput>
        </soap:Body>
    </soap:Envelope>
    """

        # Raise UserError to display the XML
        # raise UserError(xml_data)
        wsdl_url = "http://labelvantage.itl-group.com:8080/lv_web/services/CustomerOrdersService?wsdl"
        session = Session()
        session.auth = HTTPBasicAuth("brandixws", "brandixws01")
        client = Client(wsdl_url, transport=Transport(session=session))
        # Send the request and get the response
        try:
            response = client.service.createCustomerOrders(
                system="live",
                usercode="brandixws",
                userpass="brandixws01",
                xmlinput=xml_data,
            )
            # Create a wizard to display the response
            wizard = self.env["rfid.response.wizard"].create(
                {"response_content": response}
            )
            self._process_response(response)  # Call the response processing method

            return {
                "type": "ir.actions.act_window",
                "res_model": "rfid.response.wizard",
                "view_mode": "form",
                "view_id": self.env.ref(
                    "ITL_LBX_MS_V2.view_rfid_response_wizard_form"
                ).id,
                "target": "new",
                "res_id": wizard.id,
            }
        except Exception as e:
            raise UserError(f"An error occurred while sending the request:\n{str(e)}")

            # raise UserError(f"Response from the service:\n{response}")

    def _process_response(self, response):
        root = ET.fromstring(response)
        for result in root.findall(".//result"):
            customer_order_no = result.find("customer_order_no").text
            status = result.find("status").text

            # Determine the new status
            if status == "error":
                new_status = "Open"
            elif status == "success":
                new_status = "Success"
            else:
                continue

            self._update_po_status(customer_order_no, new_status)

    def _update_po_status(self, customer_order_no, new_status):
        # Search for the corresponding PO line in the Odoo model
        po_line = self.env["get_po_mas_lines_main_lable"].search(
            [("POwithLine", "=", customer_order_no)]
        )
        if po_line:

            current_status = po_line.mapped("StatusField")
            if "Success" in current_status:
                return
            po_line.write({"StatusField": new_status})

        else:
            raise UserError(f"PO with line {customer_order_no} not found.")

    # <----- XML ---->
    def action_main_xml(self):
        lines = self.env["get_po_mas_lines_main_lable"].search(
            [("header_table", "=", self.id)]
        )

        if not lines:
            raise UserError("No lines found for the given header.")

        ChainID_id = lines[0].ChainID_id if lines[0].ChainID_id else ""
        CustomerID = lines[0].CustomerID if lines[0].CustomerID else ""
        AddressID = lines[0].AddressID if lines[0].AddressID else ""
        Customer_name = lines[0].Customer_name if lines[0].Customer_name else ""
        po_number = lines[0].po_number if lines[0].po_number else ""
        # customer_style = lines[0].customer_style if lines[0].customer_style else ""
        # po_date = lines[0].po_date if lines[0].po_date else ""
        # style_number = lines[0].style_number if lines[0].style_number else ""
        # purchase_order_item = (
        #     lines[0].purchase_order_item if lines[0].purchase_order_item else ""
        # )
        # vendor_id = lines[0].vendor_id if lines[0].vendor_id else ""
        # FactoryID = lines[0].FactoryID if lines[0].FactoryID else ""
        # Group by POwithLine
        orders = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        so_ref_lvs = {}
        po_dates = {}
        style_nos = {}
        purchase_order_items = {}
        vendor_ids = {}
        date_of_manufacture_last_four_letters_all = {}
        Country = {}
        order_quantities = {}
        color_descr = {}
        vss_nos = {}
        vsd_style_6s = {}
        vsd_style_9s = {}
        RnNumbers = {}
        CaNumbers = {}
        for line in lines:
            POwithLine = line.POwithLine
            orders[line.POwithLine][
                line.ProductRef,
                line.season,
                line.material_code,
                line.FactoryID,
                line.silhouette,
                line.Collection,
                line.size_range,
            ][line.grid_value].append(line)
            if POwithLine not in so_ref_lvs:
                so_ref_lvs[POwithLine] = line.SoRefLv or ""
            if POwithLine not in po_dates:
                po_dates[POwithLine] = line.po_date or ""
            if POwithLine not in style_nos:
                style_nos[POwithLine] = line.style_number or ""
            if POwithLine not in purchase_order_items:
                purchase_order_items[POwithLine] = line.purchase_order_item or ""
            if POwithLine not in vendor_ids:
                vendor_ids[POwithLine] = line.vendor_id or ""
            if POwithLine not in date_of_manufacture_last_four_letters_all:
                date_of_manufacture_last_four_letters_all[POwithLine] = (
                    line.date_of_manufacture_last_four_letters or ""
                )
            if POwithLine not in Country:
                Country[POwithLine] = line.Coo or ""
            if POwithLine not in order_quantities:
                order_quantities[POwithLine] = line.order_quantity or ""

            if POwithLine not in color_descr:
                color_descr[POwithLine] = line.color_desc or ""

            if POwithLine not in vss_nos:
                vss_nos[POwithLine] = line.vss_no or ""

            if POwithLine not in vsd_style_6s:
                vsd_style_6s[POwithLine] = line.vsd_style_6 or ""

            if POwithLine not in vsd_style_9s:
                vsd_style_9s[POwithLine] = line.vsd_style_9 or ""

            if POwithLine not in RnNumbers:
                RnNumbers[POwithLine] = line.RnNumber or ""

            if POwithLine not in CaNumbers:
                CaNumbers[POwithLine] = line.CaNumber or ""
        # Start building the XML with formatting
        xml_body = "<customerorders>\n"

        for POwithLine, worksorders in orders.items():
            xml_body += "    <customerorder>\n"
            xml_body += f"        <itlcode>3</itlcode>\n"
            xml_body += f"         <chainid>{ChainID_id}</chainid>\n"
            xml_body += f"        <ocscustno>{CustomerID}</ocscustno>\n"
            xml_body += f"        <supplier_account></supplier_account>\n"
            xml_body += f"        <paying_party></paying_party>\n"
            xml_body += f"        <customer_order_no>{POwithLine}</customer_order_no>\n"
            xml_body += f"        <invoice_phone></invoice_phone>\n"
            xml_body += (
                f"        <delivery_address_id>{AddressID}</delivery_address_id>\n"
            )
            xml_body += (
                f"        <delivery_contact>{Customer_name}</delivery_contact>\n"
            )
            xml_body += f"        <delivery_method>TRUCK</delivery_method>\n"
            xml_body += f"        <delivery_account_no></delivery_account_no>\n"
            xml_body += (
                f"        <customer_confirmation_email></customer_confirmation_email>\n"
            )
            xml_body += f"        <comments></comments>\n"
            xml_body += f"        <quotation></quotation>\n"
            xml_body += "        <worksorders>\n"

            for (
                ProductRef,
                season,
                material_code,
                FactoryID,
                silhouette,
                Collection,
                size_range,
            ), sizelines in worksorders.items():
                xml_body += "            <worksorder>\n"
                xml_body += f"                <product_ref>{ProductRef}</product_ref>\n"
                xml_body += (
                    f"                <vs_po_number>{po_number}</vs_po_number>\n"
                )
                xml_body += (
                    f"                <po_date>{po_dates[POwithLine]}</po_date>\n"
                )
                xml_body += f"                <style_number>{style_nos[POwithLine]}</style_number>\n"
                xml_body += f"                <colour_descr>{color_descr[POwithLine]}</colour_descr>\n"
                xml_body += f"                <line_item>{purchase_order_items[POwithLine]}</line_item>\n"
                xml_body += (
                    f"                <so_number>{so_ref_lvs[POwithLine]}</so_number>\n"
                )
                xml_body += f"                <item_code>{material_code}</item_code>\n"
                xml_body += f"                <reg_no></reg_no>\n"
                xml_body += (
                    f"                <vendor_id>{vendor_ids[POwithLine]}</vendor_id>\n"
                )
                xml_body += f"                <style_descr></style_descr>\n"
                xml_body += f"                <factory_id>{FactoryID}</factory_id>\n"
                xml_body += f"                <itl_factory_code></itl_factory_code>\n"
                xml_body += f"                <silhouette>{silhouette}</silhouette>\n"
                xml_body += f"                <collection>{Collection}</collection>\n"
                xml_body += f"                <colour></colour>\n"  # need to discuss
                xml_body += f"                <vs_stores></vs_stores>\n"
                xml_body += f"                <vss_no>{vss_nos[POwithLine]}</vss_no>\n"
                xml_body += f"                <vsd_style_6>{vsd_style_6s[POwithLine]}</vsd_style_6>\n"
                xml_body += f"                <vsd_style_9>{vsd_style_9s[POwithLine]}</vsd_style_9>\n"
                xml_body += (
                    f"                <rn_number>{RnNumbers[POwithLine]}</rn_number>\n"
                )
                xml_body += (
                    f"                <ca_number>{CaNumbers[POwithLine]}</ca_number>\n"
                )
                xml_body += f"                <season>{season}</season>\n"
                xml_body += f"                <date_of_manuf>{date_of_manufacture_last_four_letters_all[POwithLine]}</date_of_manuf>\n"
                xml_body += f"                <country_of_origin>{Country[POwithLine]}</country_of_origin>\n"
                xml_body += f"                <order_quantity>{order_quantities[POwithLine]}</order_quantity>\n"
                xml_body += f"                <size_range>{size_range}</size_range>\n"
                xml_body += "                <sizelines>\n"

                for size, size_lines in sizelines.items():
                    xml_body += "                    <size_line>\n"
                    size_value = (
                        size_lines[0].size_lv if size_lines[0].size_lv else size
                    )
                    # xml_body += f"                        <size>{size}</size>\n"
                    xml_body += f"                        <size>{size_value}</size>\n"

                    # xml_body += f"                        <size_id>{size_lines[0].size_id}</size_id>\n"
                    xml_body += (
                        f"                        <po_number>{po_number}</po_number>\n"
                    )
                    customer_style = (
                        size_lines[0].customer_style
                        if size_lines[0].customer_style
                        else ""
                    )
                    xml_body += (
                        f"                        <style>{customer_style}</style>\n"
                    )
                    xml_body += f"                        <colour_code>{size_lines[0].color_code_2}</colour_code>\n"
                    xml_body += (
                        f"                        <panty_length></panty_length>\n"
                    )
                    xml_body += f"                        <desc>{size_lines[0].material_description}</desc>\n"
                    xml_body += f"                        <delivery_date>{size_lines[0].DelDate}</delivery_date>\n"
                    xml_body += f"                        <size_quantity>{size_lines[0].size_quantity}</size_quantity>\n"

                    xml_body += "                    </size_line>\n"

                xml_body += "                </sizelines>\n"
                # xml_body += "                <additional_instructions>\n"
                # for size, size_lines in sizelines.items():
                #     for line in size_lines:
                #         if line.additional_ins:
                #             # additional_instructions shoudl come bottom of the lines
                #             xml_body += f"                    <additional_instruction>{line.additional_ins}</additional_instruction>\n"

                # xml_body += "                </additional_instructions>\n"
                xml_body += "                <care_instruction_sets>\n"

                for size, size_lines in sizelines.items():
                    for line in size_lines:
                        if line.care_instruction_set_code:
                            xml_body += f"                    <care_instruction_set_code>{line.care_instruction_set_code}</care_instruction_set_code>\n"
                # xml_body += "                    <care_instruction_set_code></care_instruction_set_code>\n"
                xml_body += "                </care_instruction_sets>\n"
                xml_body += "                <additional_care_instructions>\n"
                for size, size_lines in sizelines.items():
                    for line in size_lines:
                        if line.additional_care_instruction:
                            # xml_body += f"                    <additional_care_instruction></additional_care_instruction>\n"
                            xml_body += f"                    <care_phrase>{line.additional_care_instruction}</care_phrase>\n"
                xml_body += "                </additional_care_instructions>\n"
                xml_body += "                <components>\n"
                try:
                    for size_line in size_lines:
                        composition = self.env["composition_master"].search(
                            [("id", "=", size_line.cid)], limit=1
                        )
                        if composition:

                            if composition.Component_1_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_1_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_1_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_1_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # except Exception as e:
                            # raise UserError(f"An error occurred: {str(e)}")

                            if composition.Component_2_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_2_name}</component_name>\n"
                            xml_body += "                        <fibres>\n"
                            if composition.component_2_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_2_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 3

                            if composition.Component_3_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_3_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_3_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_3_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 4

                            if composition.Component_4_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_4_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_4_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_4_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 5

                            if composition.Component_5_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_5_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_5_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_5_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 6

                            if composition.Component_6_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_6_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_6_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_6_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 7

                            if composition.Component_7_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_7_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_7_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_7_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 8

                            if composition.Component_8_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_8_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_8_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_8_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 9

                            if composition.Component_9_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_9_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_9_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_9_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 10

                            if composition.Component_10_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_10_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_10_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_10_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                except Exception as e:
                    raise UserError(f"An error occurred: {str(e)}")

                xml_body += "                </components>\n"
                xml_body += "                <additional_instructions>\n"
                for size, size_lines in sizelines.items():
                    for line in size_lines:
                        if line.additional_ins:
                            # additional_instructions shoudl come bottom of the lines
                            xml_body += f"                    <additional_instruction>{line.additional_ins}</additional_instruction>\n"

                xml_body += "                </additional_instructions>\n"
                xml_body += "            </worksorder>\n"

            xml_body += "        </worksorders>\n"
            xml_body += "    </customerorder>\n"

        xml_body += "</customerorders>"

        # Complete XML structure with formatting
        xml_data = f"""<?xml version='1.0' encoding='UTF-8'?>
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
        <soap:Header />
        <soap:Body>
            <ser:xmlinput xmlns:ser="http://services.web.labelvantage.com">
                <![CDATA[
    {xml_body}
                ]]>
            </ser:xmlinput>
        </soap:Body>
    </soap:Envelope>
    """

        # Raise UserError to display the XML
        raise UserError(xml_data)

    #

    # ----------------------------------------------------------------------------------------------------------
    # Prize Tkt - Posting
    # ----------------------------------------------------------------------------------------------------------
    xml_content = fields.Binary("XML Content", readonly=True)

    def action_post_prize(self):
        customer_orders = {}
        lines = self.env["get_po_mas_lines_price_tkt"].search(
            [("header_table", "=", self.id)]
        )

        # for line in self.line_ids:
        for line in lines:
            if line.POwithLine not in customer_orders:
                customer_orders[line.POwithLine] = {
                    "details": {
                        "itlcode": "3",
                        "chainid": line.ChainID_id,
                        "ocscustno": line.CustomerID,
                        "delivery_address_id": line.AddressID,
                        "delivery_contact": line.Customer_name,
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
                        "order_quantity": line.order_quantity,
                        "season": line.season,
                        "size_range": line.size_range,
                        "country_of_origin": line.Coo,
                    },
                    "sizes": [],
                }

            customer_orders[line.POwithLine]["orders"][line.ProductRef]["sizes"].append(
                {
                    "size": line.size_lv if line.size_lv else line.grid_value,
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
                    "size_quantity": line.size_quantity,
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

                    # size_column = "size_lv" if "size_lv" in size_data else "size"
                    size_elem = ET.SubElement(size_line_elem, "size")
                    size_elem.text = size_data["size"]  # check

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

        # request sending
        response = client.service.createCustomerOrders(
            system="test",
            usercode="brandixws",
            userpass="brandixws01",
            xmlinput=pretty_xml_str_rfid,
        )
        wizard = self.env["rfid.response.wizard"].create({"response_content": response})
        self._process_response(response)
        return {
            "type": "ir.actions.act_window",
            "res_model": "rfid.response.wizard",
            "view_mode": "form",
            "view_id": self.env.ref("ITL_LBX_MS_V2.view_rfid_response_wizard_form").id,
            "target": "new",
            "res_id": wizard.id,
        }

    def _process_response(self, response):
        # parsing the response
        root = ET.fromstring(response)

        # Iterate over each result
        for result in root.findall("result"):
            status = result.find("status").text
            customer_order_no = result.find("customer_order_no").text

            # Determine the new status
            if status == "error":
                new_status = "Open"
            elif status == "success":
                new_status = "Success"
            else:
                continue

            # Update the status in Odoo
            self._update_po_status(customer_order_no, new_status)

    def _update_po_status(self, customer_order_no, new_status):
        po_lines = self.env["get_po_mas_lines_price_tkt"].search(
            [("POwithLine", "=", customer_order_no)]
        )
        if po_lines:
            # Check if the current status is already 'Success'
            current_status = po_lines.mapped("StatusField")
            if "Success" in current_status:
                # If any line already has a status of 'Success', do not update it
                return
            po_lines.write({"StatusField": new_status})
        else:
            raise UserError(f"PO with line {customer_order_no} not found.")

    # ----------------------------------------------------------------------------------------------------------
    # RFID - XML
    # ----------------------------------------------------------------------------------------------------------
    xml_content = fields.Binary("XML Content", readonly=True)

    def action_check_prize(self):
        customer_orders = {}
        lines = self.env["get_po_mas_lines_price_tkt"].search(
            [("header_table", "=", self.id)]
        )

        # for line in self.line_ids:
        for line in lines:
            if line.POwithLine not in customer_orders:
                customer_orders[line.POwithLine] = {
                    "details": {
                        "itlcode": "3",
                        "chainid": line.ChainID_id,
                        "ocscustno": line.CustomerID,
                        "delivery_address_id": line.AddressID,
                        "delivery_contact": line.Customer_name,
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
                        "order_quantity": line.order_quantity,
                        "season": line.season,
                        "size_range": line.size_range,
                        "country_of_origin": line.Coo,
                    },
                    "sizes": [],
                }

            customer_orders[line.POwithLine]["orders"][line.ProductRef]["sizes"].append(
                {
                    "size": line.size_lv if line.size_lv else line.grid_value,
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
                    "size_quantity": line.size_quantity,
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

                    # size_column = "size_lv" if "size_lv" in size_data else "size"
                    size_elem = ET.SubElement(size_line_elem, "size")
                    size_elem.text = size_data["size"]  # check

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

    # -----------------------------------------------------------------------------------------------------------
    # Care Label - Post
    # -----------------------------------------------------------------------------------------------------------

    def action_post_care(self):
        lines = self.env["get_po_mas_lines_care_lable"].search(
            [("header_table", "=", self.id)]
        )

        if not lines:
            raise UserError("No lines found for the given header.")

        ChainID_id = lines[0].ChainID_id if lines[0].ChainID_id else ""
        CustomerID = lines[0].CustomerID if lines[0].CustomerID else ""
        AddressID = lines[0].AddressID if lines[0].AddressID else ""
        Customer_name = lines[0].Customer_name if lines[0].Customer_name else ""
        po_number = lines[0].po_number if lines[0].po_number else ""
        # customer_style = lines[0].customer_style if lines[0].customer_style else ""
        # po_date = lines[0].po_date if lines[0].po_date else ""
        # style_number = lines[0].style_number if lines[0].style_number else ""
        # purchase_order_item = (
        #     lines[0].purchase_order_item if lines[0].purchase_order_item else ""
        # )
        # vendor_id = lines[0].vendor_id if lines[0].vendor_id else ""
        # FactoryID = lines[0].FactoryID if lines[0].FactoryID else ""
        # Group by POwithLine
        orders = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        so_ref_lvs = {}
        po_dates = {}
        style_nos = {}
        purchase_order_items = {}
        vendor_ids = {}
        date_of_manufacture_last_four_letters_all = {}
        Country = {}
        order_quantities = {}
        color_descr = {}
        vss_nos = {}
        vsd_style_6s = {}
        vsd_style_9s = {}
        RnNumbers = {}
        CaNumbers = {}
        for line in lines:
            POwithLine = line.POwithLine
            orders[line.POwithLine][
                line.ProductRef,
                line.season,
                line.material_code,
                line.FactoryID,
                line.silhouette,
                line.Collection,
                line.size_range,
            ][line.grid_value].append(line)
            if POwithLine not in so_ref_lvs:
                so_ref_lvs[POwithLine] = line.SoRefLv or ""
            if POwithLine not in po_dates:
                po_dates[POwithLine] = line.po_date or ""
            if POwithLine not in style_nos:
                style_nos[POwithLine] = line.style_number or ""
            if POwithLine not in purchase_order_items:
                purchase_order_items[POwithLine] = line.purchase_order_item or ""
            if POwithLine not in vendor_ids:
                vendor_ids[POwithLine] = line.vendor_id or ""
            if POwithLine not in date_of_manufacture_last_four_letters_all:
                date_of_manufacture_last_four_letters_all[POwithLine] = (
                    line.date_of_manufacture_last_four_letters or ""
                )
            if POwithLine not in Country:
                Country[POwithLine] = line.Coo or ""
            if POwithLine not in order_quantities:
                order_quantities[POwithLine] = line.order_quantity or ""

            if POwithLine not in color_descr:
                color_descr[POwithLine] = line.color_desc or ""

            if POwithLine not in vss_nos:
                vss_nos[POwithLine] = line.vss_no or ""

            if POwithLine not in vsd_style_6s:
                vsd_style_6s[POwithLine] = line.vsd_style_6 or ""

            if POwithLine not in vsd_style_9s:
                vsd_style_9s[POwithLine] = line.vsd_style_9 or ""

            if POwithLine not in RnNumbers:
                RnNumbers[POwithLine] = line.RnNumber or ""

            if POwithLine not in CaNumbers:
                CaNumbers[POwithLine] = line.CaNumber or ""
        # Start building the XML with formatting
        xml_body = "<customerorders>\n"

        for POwithLine, worksorders in orders.items():
            xml_body += "    <customerorder>\n"
            xml_body += f"        <itlcode>3</itlcode>\n"
            xml_body += f"         <chainid>{ChainID_id}</chainid>\n"
            xml_body += f"        <ocscustno>{CustomerID}</ocscustno>\n"
            xml_body += f"        <supplier_account></supplier_account>\n"
            xml_body += f"        <paying_party></paying_party>\n"
            xml_body += f"        <customer_order_no>{POwithLine}</customer_order_no>\n"
            xml_body += f"        <invoice_phone></invoice_phone>\n"
            xml_body += (
                f"        <delivery_address_id>{AddressID}</delivery_address_id>\n"
            )
            xml_body += (
                f"        <delivery_contact>{Customer_name}</delivery_contact>\n"
            )
            xml_body += f"        <delivery_method>TRUCK</delivery_method>\n"
            xml_body += f"        <delivery_account_no>ITL</delivery_account_no>\n"
            xml_body += (
                f"        <customer_confirmation_email></customer_confirmation_email>\n"
            )
            xml_body += f"        <comments></comments>\n"
            xml_body += f"        <quotation></quotation>\n"
            xml_body += "        <worksorders>\n"

            for (
                ProductRef,
                season,
                material_code,
                FactoryID,
                silhouette,
                Collection,
                size_range,
            ), sizelines in worksorders.items():
                xml_body += "            <worksorder>\n"
                xml_body += f"                <product_ref>{ProductRef}</product_ref>\n"
                xml_body += (
                    f"                <vs_po_number>{po_number}</vs_po_number>\n"
                )
                xml_body += (
                    f"                <po_date>{po_dates[POwithLine]}</po_date>\n"
                )
                xml_body += f"                <style_number>{style_nos[POwithLine]}</style_number>\n"
                xml_body += f"                <colour_descr>{color_descr[POwithLine]}</colour_descr>\n"
                xml_body += f"                <line_item>{purchase_order_items[POwithLine]}</line_item>\n"
                xml_body += (
                    f"                <so_number>{so_ref_lvs[POwithLine]}</so_number>\n"
                )
                xml_body += f"                <item_code>{material_code}</item_code>\n"
                xml_body += f"                <reg_no></reg_no>\n"
                xml_body += (
                    f"                <vendor_id>{vendor_ids[POwithLine]}</vendor_id>\n"
                )
                xml_body += f"                <style_descr></style_descr>\n"
                xml_body += f"                <factory_id>{FactoryID}</factory_id>\n"
                xml_body += f"                <itl_factory_code></itl_factory_code>\n"
                xml_body += f"                <silhouette>{silhouette}</silhouette>\n"
                xml_body += f"                <collection>{Collection}</collection>\n"
                xml_body += f"                <colour></colour>\n"  # need to discuss
                xml_body += f"                <vs_stores></vs_stores>\n"
                xml_body += f"                <vss_no>{vss_nos[POwithLine]}</vss_no>\n"
                xml_body += f"                <vsd_style_6>{vsd_style_6s[POwithLine]}</vsd_style_6>\n"
                xml_body += f"                <vsd_style_9>{vsd_style_9s[POwithLine]}</vsd_style_9>\n"
                xml_body += (
                    f"                <rn_number>{RnNumbers[POwithLine]}</rn_number>\n"
                )
                xml_body += (
                    f"                <ca_number>{CaNumbers[POwithLine]}</ca_number>\n"
                )
                xml_body += f"                <season>{season}</season>\n"
                xml_body += f"                <date_of_manuf>{date_of_manufacture_last_four_letters_all[POwithLine]}</date_of_manuf>\n"
                xml_body += f"                <country_of_origin>{Country[POwithLine]}</country_of_origin>\n"
                xml_body += f"                <order_quantity>{order_quantities[POwithLine]}</order_quantity>\n"
                xml_body += f"                <size_range>{size_range}</size_range>\n"
                xml_body += "                <sizelines>\n"

                for size, size_lines in sizelines.items():
                    xml_body += "                    <size_line>\n"
                    size_value = (
                        size_lines[0].size_lv if size_lines[0].size_lv else size
                    )
                    # xml_body += f"                        <size>{size}</size>\n"
                    xml_body += f"                        <size>{size_value}</size>\n"

                    # xml_body += f"                        <size_id>{size_lines[0].size_id}</size_id>\n"
                    xml_body += (
                        f"                        <po_number>{po_number}</po_number>\n"
                    )
                    customer_style = (
                        size_lines[0].customer_style
                        if size_lines[0].customer_style
                        else ""
                    )
                    xml_body += (
                        f"                        <style>{customer_style}</style>\n"
                    )
                    xml_body += f"                        <colour_code>{size_lines[0].color_code_2}</colour_code>\n"
                    xml_body += (
                        f"                        <panty_length></panty_length>\n"
                    )
                    xml_body += f"                        <desc>{size_lines[0].material_description}</desc>\n"
                    xml_body += f"                        <delivery_date>{size_lines[0].DelDate}</delivery_date>\n"
                    xml_body += f"                        <size_quantity>{size_lines[0].size_quantity}</size_quantity>\n"

                    xml_body += "                    </size_line>\n"

                xml_body += "                </sizelines>\n"
                # xml_body += "                <additional_instructions>\n"
                # for size, size_lines in sizelines.items():
                #     for line in size_lines:
                #         if line.additional_ins:
                #             # additional_instructions shoudl come bottom of the lines
                #             xml_body += f"                    <additional_instruction>{line.additional_ins}</additional_instruction>\n"

                # xml_body += "                </additional_instructions>\n"
                xml_body += "                <care_instruction_sets>\n"

                for size, size_lines in sizelines.items():
                    for line in size_lines:
                        if line.care_instruction_set_code:
                            xml_body += f"                    <care_instruction_set_code>{line.care_instruction_set_code}</care_instruction_set_code>\n"
                # xml_body += "                    <care_instruction_set_code></care_instruction_set_code>\n"
                xml_body += "                </care_instruction_sets>\n"
                xml_body += "                <additional_care_instructions>\n"
                for size, size_lines in sizelines.items():
                    for line in size_lines:
                        if line.additional_care_instruction:
                            # xml_body += f"                    <additional_care_instruction></additional_care_instruction>\n"
                            xml_body += f"                    <care_phrase>{line.additional_care_instruction}</care_phrase>\n"
                xml_body += "                </additional_care_instructions>\n"
                xml_body += "                <components>\n"
                try:
                    for size_line in size_lines:
                        composition = self.env["composition_master"].search(
                            [("id", "=", size_line.cid)], limit=1
                        )
                        if composition:
                            if composition.Component_1_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_1_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_1_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_1_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # except Exception as e:
                            # raise UserError(f"An error occurred: {str(e)}")
                            # Component2
                            if composition.Component_2_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_2_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_2_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_2_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"

                            # component 3

                            if composition.Component_3_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_3_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_3_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_3_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"

                            # component 4
                            if composition.Component_4_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_4_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_4_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_4_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"

                            # component 5
                            if composition.Component_5_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_5_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_5_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_5_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 6

                            if composition.Component_6_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_6_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_6_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_6_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"

                            # component 7

                            if composition.Component_7_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_7_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_7_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_7_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"

                            # component 8

                            if composition.Component_8_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_8_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_8_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_8_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"

                            # component 9

                            if composition.Component_9_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_9_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_9_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_9_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 10

                            if composition.Component_10_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_10_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_10_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_10_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                except Exception as e:
                    raise UserError(f"An error occurred: {str(e)}")

                xml_body += "                </components>\n"
                xml_body += "                <additional_instructions>\n"
                for size, size_lines in sizelines.items():
                    for line in size_lines:
                        if line.additional_ins:
                            # additional_instructions shoudl come bottom of the lines
                            xml_body += f"                    <additional_instruction>{line.additional_ins}</additional_instruction>\n"

                xml_body += "                </additional_instructions>\n"
                xml_body += "            </worksorder>\n"

            xml_body += "        </worksorders>\n"
            xml_body += "    </customerorder>\n"

        xml_body += "</customerorders>"

        # Complete XML structure with formatting
        xml_data = f"""<?xml version='1.0' encoding='UTF-8'?>
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
        <soap:Header />
        <soap:Body>
            <ser:xmlinput xmlns:ser="http://services.web.labelvantage.com">
                <![CDATA[
    {xml_body}
                ]]>
            </ser:xmlinput>
        </soap:Body>
    </soap:Envelope>
    """

        # Raise UserError to display the XML
        # raise UserError(xml_data)
        wsdl_url = "http://labelvantage.itl-group.com:8080/lv_web/services/CustomerOrdersService?wsdl"
        session = Session()
        session.auth = HTTPBasicAuth("brandixws", "brandixws01")
        client = Client(wsdl_url, transport=Transport(session=session))
        # Send the request and get the response
        try:
            response = client.service.createCustomerOrders(
                system="live",
                usercode="brandixws",
                userpass="brandixws01",
                xmlinput=xml_data,
            )
            # Create a wizard to display the response
            wizard = self.env["rfid.response.wizard"].create(
                {"response_content": response}
            )
            self._process_response(response)  # Call the response processing method

            return {
                "type": "ir.actions.act_window",
                "res_model": "rfid.response.wizard",
                "view_mode": "form",
                "view_id": self.env.ref(
                    "ITL_LBX_MS_V2.view_rfid_response_wizard_form"
                ).id,
                "target": "new",
                "res_id": wizard.id,
            }
        except Exception as e:
            raise UserError(f"An error occurred while sending the request:\n{str(e)}")

            # raise UserError(f"Response from the service:\n{response}")

    def _process_response(self, response):
        root = ET.fromstring(response)
        for result in root.findall(".//result"):
            customer_order_no = result.find("customer_order_no").text
            status = result.find("status").text

            # Determine the new status
            if status == "error":
                new_status = "Open"
            elif status == "success":
                new_status = "Success"
            else:
                continue

            self._update_po_status(customer_order_no, new_status)

    def _update_po_status(self, customer_order_no, new_status):
        # Search for the corresponding PO line in the Odoo model
        po_line = self.env["get_po_mas_lines_care_lable"].search(
            [("POwithLine", "=", customer_order_no)]
        )
        if po_line:

            current_status = po_line.mapped("StatusField")
            if "Success" in current_status:
                return
            po_line.write({"StatusField": new_status})

        else:
            raise UserError(f"PO with line {customer_order_no} not found.")

    # <----- XML ---->
    def action_care_xml(self):
        lines = self.env["get_po_mas_lines_care_lable"].search(
            [("header_table", "=", self.id)]
        )

        if not lines:
            raise UserError("No lines found for the given header.")

        ChainID_id = lines[0].ChainID_id if lines[0].ChainID_id else ""
        CustomerID = lines[0].CustomerID if lines[0].CustomerID else ""
        AddressID = lines[0].AddressID if lines[0].AddressID else ""
        Customer_name = lines[0].Customer_name if lines[0].Customer_name else ""
        po_number = lines[0].po_number if lines[0].po_number else ""
        # customer_style = lines[0].customer_style if lines[0].customer_style else ""
        # po_date = lines[0].po_date if lines[0].po_date else ""
        # style_number = lines[0].style_number if lines[0].style_number else ""
        # purchase_order_item = (
        #     lines[0].purchase_order_item if lines[0].purchase_order_item else ""
        # )
        # vendor_id = lines[0].vendor_id if lines[0].vendor_id else ""
        # FactoryID = lines[0].FactoryID if lines[0].FactoryID else ""
        # Group by POwithLine
        orders = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))
        so_ref_lvs = {}
        po_dates = {}
        style_nos = {}
        purchase_order_items = {}
        vendor_ids = {}
        date_of_manufacture_last_four_letters_all = {}
        Country = {}
        order_quantities = {}
        color_descr = {}
        vss_nos = {}
        vsd_style_6s = {}
        vsd_style_9s = {}
        RnNumbers = {}
        CaNumbers = {}
        for line in lines:
            POwithLine = line.POwithLine
            orders[line.POwithLine][
                line.ProductRef,
                line.season,
                line.material_code,
                line.FactoryID,
                line.silhouette,
                line.Collection,
                line.size_range,
            ][line.grid_value].append(line)
            if POwithLine not in so_ref_lvs:
                so_ref_lvs[POwithLine] = line.SoRefLv or ""
            if POwithLine not in po_dates:
                po_dates[POwithLine] = line.po_date or ""
            if POwithLine not in style_nos:
                style_nos[POwithLine] = line.style_number or ""
            if POwithLine not in purchase_order_items:
                purchase_order_items[POwithLine] = line.purchase_order_item or ""
            if POwithLine not in vendor_ids:
                vendor_ids[POwithLine] = line.vendor_id or ""
            if POwithLine not in date_of_manufacture_last_four_letters_all:
                date_of_manufacture_last_four_letters_all[POwithLine] = (
                    line.date_of_manufacture_last_four_letters or ""
                )
            if POwithLine not in Country:
                Country[POwithLine] = line.Coo or ""
            if POwithLine not in order_quantities:
                order_quantities[POwithLine] = line.order_quantity or ""

            if POwithLine not in color_descr:
                color_descr[POwithLine] = line.color_desc or ""

            if POwithLine not in vss_nos:
                vss_nos[POwithLine] = line.vss_no or ""

            if POwithLine not in vsd_style_6s:
                vsd_style_6s[POwithLine] = line.vsd_style_6 or ""

            if POwithLine not in vsd_style_9s:
                vsd_style_9s[POwithLine] = line.vsd_style_9 or ""

            if POwithLine not in RnNumbers:
                RnNumbers[POwithLine] = line.RnNumber or ""

            if POwithLine not in CaNumbers:
                CaNumbers[POwithLine] = line.CaNumber or ""
        # Start building the XML with formatting
        xml_body = "<customerorders>\n"

        for POwithLine, worksorders in orders.items():
            xml_body += "    <customerorder>\n"
            xml_body += f"        <itlcode>3</itlcode>\n"
            xml_body += f"         <chainid>{ChainID_id}</chainid>\n"
            xml_body += f"        <ocscustno>{CustomerID}</ocscustno>\n"
            xml_body += f"        <supplier_account></supplier_account>\n"
            xml_body += f"        <paying_party></paying_party>\n"
            xml_body += f"        <customer_order_no>{POwithLine}</customer_order_no>\n"
            xml_body += f"        <invoice_phone></invoice_phone>\n"
            xml_body += (
                f"        <delivery_address_id>{AddressID}</delivery_address_id>\n"
            )
            xml_body += (
                f"        <delivery_contact>{Customer_name}</delivery_contact>\n"
            )
            xml_body += f"        <delivery_method>TRUCK</delivery_method>\n"
            xml_body += f"        <delivery_account_no></delivery_account_no>\n"
            xml_body += (
                f"        <customer_confirmation_email></customer_confirmation_email>\n"
            )
            xml_body += f"        <comments></comments>\n"
            xml_body += f"        <quotation></quotation>\n"
            xml_body += "        <worksorders>\n"

            for (
                ProductRef,
                season,
                material_code,
                FactoryID,
                silhouette,
                Collection,
                size_range,
            ), sizelines in worksorders.items():
                xml_body += "            <worksorder>\n"
                xml_body += f"                <product_ref>{ProductRef}</product_ref>\n"
                xml_body += (
                    f"                <vs_po_number>{po_number}</vs_po_number>\n"
                )
                xml_body += (
                    f"                <po_date>{po_dates[POwithLine]}</po_date>\n"
                )
                xml_body += f"                <style_number>{style_nos[POwithLine]}</style_number>\n"
                xml_body += f"                <colour_descr>{color_descr[POwithLine]}</colour_descr>\n"
                xml_body += f"                <line_item>{purchase_order_items[POwithLine]}</line_item>\n"
                xml_body += (
                    f"                <so_number>{so_ref_lvs[POwithLine]}</so_number>\n"
                )
                xml_body += f"                <item_code>{material_code}</item_code>\n"
                xml_body += f"                <reg_no></reg_no>\n"
                xml_body += (
                    f"                <vendor_id>{vendor_ids[POwithLine]}</vendor_id>\n"
                )
                xml_body += f"                <style_descr></style_descr>\n"
                xml_body += f"                <factory_id>{FactoryID}</factory_id>\n"
                xml_body += f"                <itl_factory_code></itl_factory_code>\n"
                xml_body += f"                <silhouette>{silhouette}</silhouette>\n"
                xml_body += f"                <collection>{Collection}</collection>\n"
                xml_body += f"                <colour></colour>\n"  # need to discuss
                xml_body += f"                <vs_stores></vs_stores>\n"
                xml_body += f"                <vss_no>{vss_nos[POwithLine]}</vss_no>\n"
                xml_body += f"                <vsd_style_6>{vsd_style_6s[POwithLine]}</vsd_style_6>\n"
                xml_body += f"                <vsd_style_9>{vsd_style_9s[POwithLine]}</vsd_style_9>\n"
                xml_body += (
                    f"                <rn_number>{RnNumbers[POwithLine]}</rn_number>\n"
                )
                xml_body += (
                    f"                <ca_number>{CaNumbers[POwithLine]}</ca_number>\n"
                )
                xml_body += f"                <season>{season}</season>\n"
                xml_body += f"                <date_of_manuf>{date_of_manufacture_last_four_letters_all[POwithLine]}</date_of_manuf>\n"
                xml_body += f"                <country_of_origin>{Country[POwithLine]}</country_of_origin>\n"
                xml_body += f"                <order_quantity>{order_quantities[POwithLine]}</order_quantity>\n"
                xml_body += f"                <size_range>{size_range}</size_range>\n"
                xml_body += "                <sizelines>\n"

                for size, size_lines in sizelines.items():
                    xml_body += "                    <size_line>\n"
                    size_value = (
                        size_lines[0].size_lv if size_lines[0].size_lv else size
                    )
                    # xml_body += f"                        <size>{size}</size>\n"
                    xml_body += f"                        <size>{size_value}</size>\n"

                    # xml_body += f"                        <size_id>{size_lines[0].size_id}</size_id>\n"
                    xml_body += (
                        f"                        <po_number>{po_number}</po_number>\n"
                    )
                    customer_style = (
                        size_lines[0].customer_style
                        if size_lines[0].customer_style
                        else ""
                    )
                    xml_body += (
                        f"                        <style>{customer_style}</style>\n"
                    )
                    xml_body += f"                        <colour_code>{size_lines[0].color_code_2}</colour_code>\n"
                    xml_body += (
                        f"                        <panty_length></panty_length>\n"
                    )
                    xml_body += f"                        <desc>{size_lines[0].material_description}</desc>\n"
                    xml_body += f"                        <delivery_date>{size_lines[0].DelDate}</delivery_date>\n"
                    xml_body += f"                        <size_quantity>{size_lines[0].size_quantity}</size_quantity>\n"

                    xml_body += "                    </size_line>\n"

                xml_body += "                </sizelines>\n"
                # xml_body += "                <additional_instructions>\n"
                # for size, size_lines in sizelines.items():
                #     for line in size_lines:
                #         if line.additional_ins:
                #             # additional_instructions shoudl come bottom of the lines
                #             xml_body += f"                    <additional_instruction>{line.additional_ins}</additional_instruction>\n"

                # xml_body += "                </additional_instructions>\n"
                xml_body += "                <care_instruction_sets>\n"

                for size, size_lines in sizelines.items():
                    for line in size_lines:
                        if line.care_instruction_set_code:
                            xml_body += f"                    <care_instruction_set_code>{line.care_instruction_set_code}</care_instruction_set_code>\n"
                # xml_body += "                    <care_instruction_set_code></care_instruction_set_code>\n"
                xml_body += "                </care_instruction_sets>\n"
                xml_body += "                <additional_care_instructions>\n"
                for size, size_lines in sizelines.items():
                    for line in size_lines:
                        if line.additional_care_instruction:
                            # xml_body += f"                    <additional_care_instruction></additional_care_instruction>\n"
                            xml_body += f"                    <care_phrase>{line.additional_care_instruction}</care_phrase>\n"
                xml_body += "                </additional_care_instructions>\n"
                xml_body += "                <components>\n"
                try:
                    for size_line in size_lines:
                        composition = self.env["composition_master"].search(
                            [("id", "=", size_line.cid)], limit=1
                        )
                        if composition:

                            if composition.Component_1_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_1_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_1_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_1_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_1_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_1_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_1_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # except Exception as e:
                            # raise UserError(f"An error occurred: {str(e)}")

                            if composition.Component_2_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_2_name}</component_name>\n"
                            xml_body += "                        <fibres>\n"
                            if composition.component_2_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_2_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_2_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_2_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_2_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 3

                            if composition.Component_3_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_3_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_3_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_3_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_3_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_3_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_3_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 4

                            if composition.Component_4_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_4_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_4_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_4_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_4_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_4_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_4_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 5

                            if composition.Component_5_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_5_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_5_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_5_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_5_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_5_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_5_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 6

                            if composition.Component_6_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_6_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_6_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_6_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_6_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_6_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_6_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 7

                            if composition.Component_7_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_7_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_7_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_7_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_7_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_7_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_7_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 8

                            if composition.Component_8_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_8_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_8_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_8_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_8_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_8_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_8_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 9

                            if composition.Component_9_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_9_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_9_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_9_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_9_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_9_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_9_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                            # component 10

                            if composition.Component_10_name:
                                xml_body += "                    <component>\n"
                                xml_body += f"                        <component_name>{composition.Component_10_name}</component_name>\n"
                                xml_body += "                        <fibres>\n"
                            if composition.component_10_fiber1_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber1_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber1_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber2_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber2_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber2_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber3_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber3_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber3_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber4_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber4_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber4_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber5_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber5_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber5_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber6_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber6_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber6_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber7_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber7_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber7_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber8_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber8_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber8_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber9_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber9_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber9_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.component_10_fiber10_name:
                                xml_body += "                            <fibre>\n"
                                xml_body += f"                                <fibre_name>{composition.component_10_fiber10_name}</fibre_name>\n"
                                xml_body += f"                                <fibre_percent>{composition.component_10_Fiber10_Percentage}</fibre_percent>\n"
                                xml_body += "                            </fibre>\n"
                            if composition.Component_10_name:
                                xml_body += "                        </fibres>\n"
                                xml_body += "                    </component>\n"
                except Exception as e:
                    raise UserError(f"An error occurred: {str(e)}")

                xml_body += "                </components>\n"
                xml_body += "                <additional_instructions>\n"
                for size, size_lines in sizelines.items():
                    for line in size_lines:
                        if line.additional_ins:
                            # additional_instructions shoudl come bottom of the lines
                            xml_body += f"                    <additional_instruction>{line.additional_ins}</additional_instruction>\n"

                xml_body += "                </additional_instructions>\n"
                xml_body += "            </worksorder>\n"

            xml_body += "        </worksorders>\n"
            xml_body += "    </customerorder>\n"

        xml_body += "</customerorders>"

        # Complete XML structure with formatting
        xml_data = f"""<?xml version='1.0' encoding='UTF-8'?>
    <soap:Envelope xmlns:soap="http://www.w3.org/2003/05/soap-envelope">
        <soap:Header />
        <soap:Body>
            <ser:xmlinput xmlns:ser="http://services.web.labelvantage.com">
                <![CDATA[
    {xml_body}
                ]]>
            </ser:xmlinput>
        </soap:Body>
    </soap:Envelope>
    """

        # Raise UserError to display the XML
        raise UserError(xml_data)