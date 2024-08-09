/** @odoo-module */

import { registry } from "@web/core/registry"
import { useBus, useService } from "@web/core/utils/hooks";
import { ItlCard } from "./kpi_card/kpi_card"
import { ChartRenderer } from "./chart_renderer/chart_renderer"
import { loadJS } from "@web/core/assets"
import { PoCard } from "./po_card/po_card";
const { Component, onWillStart, useRef, onMounted } = owl

export class ItlDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        onWillStart(async () => {
            await this.loadDashboardData();
        });
    }

    async loadDashboardData() {
        const context = {};
        this.purchase_order_count = await this.orm.call(
            'get_po_mas',
            'get_purchase_order_count',
            [],
            {
                context: context
            }
        );
    }
}

ItlDashboard.template = "Itl.Dashboard"
ItlDashboard.components = { ItlCard, ChartRenderer, PoCard }

registry.category("actions").add("Itl.Dashboard", ItlDashboard)