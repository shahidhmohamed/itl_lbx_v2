/* @odoo-module */
import { registry } from '@web/core/registry';
const { Component } = owl;
export class OrderDetails extends Component { }
OrderDetails.template = 'OrderDetails';
OrderDetails.props = ['data', 'label'];
registry.category("components").add('OrderDetails', OrderDetails);
