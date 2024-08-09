/* @odoo-module */
import { registry } from '@web/core/registry';
const { Component } = owl;
export class ItlCard extends Component { }
ItlCard.template = 'Itl.Card';
ItlCard.props = ['done', 'label'];
registry.category("components").add('ItlCard', ItlCard);
