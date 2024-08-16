/** @odoo-module */

const { Component } = owl

export class PoCard extends Component { }
PoCard.props = ['done', 'label'];
PoCard.template = "owl.PoCard"