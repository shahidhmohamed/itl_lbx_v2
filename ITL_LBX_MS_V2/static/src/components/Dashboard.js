/** @odoo-module */

import { registry } from "@web/core/registry"
import { useBus, useService } from "@web/core/utils/hooks";
import { ItlCard } from "./kpi_card/kpi_card"
import { loadJS } from "@web/core/assets"
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
        this.order_count = await this.orm.call(
            'get_po_mas',
            'compute_total_orders',
            [],
            {
                context: context
            }
        );
    }
}

ItlDashboard.template = "Itl.Dashboard"
ItlDashboard.components = { ItlCard }

registry.category("actions").add("Itl.Dashboard", ItlDashboard)