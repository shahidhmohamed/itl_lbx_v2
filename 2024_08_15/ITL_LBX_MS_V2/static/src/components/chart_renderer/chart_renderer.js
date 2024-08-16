/** @odoo-module */

import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
const { Component, onWillStart, useRef, onMounted } = owl;

export class ChartRenderer extends Component {
  setup() {
    this.chartRef = useRef("chart");

    onWillStart(async () => {
      await loadJS("https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js");
    });

    onMounted(() => this.renderChart());
  }

  renderChart() {
    new Chart(this.chartRef.el, {
      type: this.props.type,
      data: {
        labels: ['Success Orders', 'Cancelled Orders', 'Open Orders', 'Total Orders'],
        datasets: [{
          data: [
            this.props.success,
            this.props.cancelled,
            this.props.open,
            this.props.all
          ],
          backgroundColor: ['#4CAF50', '#FF5252', '#FFC107', '#2196F3'],
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        plugins: {
          legend: {
            position: 'bottom',
          },
          title: {
            display: true,
            text: this.props.title,
            position: 'bottom',
          }
        }
      },
    });
  }
}

ChartRenderer.template = "Itl.ChartRenderer";
