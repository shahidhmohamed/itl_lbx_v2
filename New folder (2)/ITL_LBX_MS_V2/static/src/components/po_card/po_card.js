/* @odoo-module */
import { registry } from '@web/core/registry';
const { Component } = owl;
export class PoCard extends Component { }
PoCard.template = 'Po.Card';
PoCard.props = ['done', 'label'];
registry.category("components").add('PoCard', PoCard);
