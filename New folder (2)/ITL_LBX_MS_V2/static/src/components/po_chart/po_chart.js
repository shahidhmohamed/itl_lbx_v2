/** @odoo-module */

import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
const { Component, onWillStart, useRef, onMounted } = owl;

export class PoChartRenderer extends Component {
  setup() {
    this.chartRef = useRef("chart");

    onWillStart(async () => {
      await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js");
    });

    onMounted(() => this.renderChart());
  }

  renderChart() {
    console.log("RFID:", this.props.rfid);
    console.log("MAIN_LABEL:", this.props.main_lable);
    console.log("CARE_LABEL:", this.props.care_lable);
    console.log("PRICE_TKT:", this.props.price_tkt);

    new Chart(this.chartRef.el, {
      type: this.props.type,  // This will now use 'bar' as the chart type
      data: {
        labels: ['RFID', 'MAIN LABEL', 'CARE LABEL', 'PRICE TKT'],
        datasets: [{
          data: [
            this.props.rfid,
            this.props.main_lable,
            this.props.care_lable,
            this.props.price_tkt
          ],
          backgroundColor: ['#4CAF50', '#FF5252', '#FFC107', '#2196F3'],
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            display: false,  // Hide the legend for a bar chart
          },
          title: {
            display: true,
            text: this.props.title,
            position: 'top',
          }
        },
        scales: {
          y: {
            beginAtZero: true
          }
        }
      },
    });
  }
}

PoChartRenderer.template = "Po.ChartRenderer";
