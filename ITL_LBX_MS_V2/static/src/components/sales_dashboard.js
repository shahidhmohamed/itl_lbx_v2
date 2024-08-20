/** @odoo-module */

import { registry } from "@web/core/registry";
import { KpiCard } from "./kpi_card/kpi_card";
import { useBus, useService } from "@web/core/utils/hooks";
import { ChartRenderer } from "./chart_renderer/chart_renderer";
import { PoChartRenderer } from "./po_type_chart/po_chart";
import { loadJS } from "@web/core/assets";
import { PoCard } from "./po_type_card/po_card";
import { RadialProgressBar } from "./line_renderer/line_renderer";
import { Percentage } from "./order_percentage_details/order_percentage_details";
import { PoPercentage } from "./po_type_percentage_details/po_type_percentage_details";
import { UserDetails } from "./user_details/user_details";
import { UserDetailsPercentage } from "./user_percentage/user_percentage";
const { Component, onWillStart, useRef, useState } = owl;

export class OwlSalesDashboard extends Component {
    setup() {
        this.orm = useService("orm");
        this.state = useState({
            chartType: 'doughnut',
        });
        this.state_2 = useState({
            chartType: 'doughnut',
        });

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

    showChart(type) {
        // Toggle between 'doughnut' and 'pie'
        this.state.chartType = (this.state.chartType === type) ? '' : type;
    }

    showChart_2(type) {
        // Toggle between 'doughnut' and 'pie'
        this.state_2.chartType = (this.state_2.chartType === type) ? '' : type;
    }
}

OwlSalesDashboard.template = "owl.OwlSalesDashboard";
OwlSalesDashboard.components = { KpiCard, ChartRenderer, PoCard, PoChartRenderer, RadialProgressBar, Percentage, PoPercentage, UserDetails, UserDetailsPercentage };

registry.category("actions").add("owl.sales_dashboard", OwlSalesDashboard);
