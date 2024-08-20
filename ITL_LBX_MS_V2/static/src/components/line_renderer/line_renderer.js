/** @odoo-module */

import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
const { Component, useRef, onMounted, useState } = owl;

export class RadialProgressBar extends Component {
  setup() {
    this.chartRef = useRef('chart');
    this.state = useState({
      percentage: this.props.percentage || 0, // Use the passed percentage or default to 0
      label: this.props.label || '', // Use the passed label or default to an empty string
    });

    onMounted(() => this.renderChart());
  }

  async renderChart() {
    // Load Chart.js and Chart.js datalabels plugin if not already loaded
    await Promise.all([
      loadJS('https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js'),
      loadJS('https://cdnjs.cloudflare.com/ajax/libs/chartjs-plugin-datalabels/2.0.0/chartjs-plugin-datalabels.min.js')
    ]);

    // Ensure Chart.js is available
    if (!window.Chart) {
      console.error('Chart.js is not loaded');
      return;
    }

    // Ensure chartjs-plugin-datalabels is available
    if (!window.ChartDataLabels) {
      console.error('chartjs-plugin-datalabels is not loaded');
      return;
    }

    // Get the canvas context
    const ctx = this.chartRef.el.getContext('2d');

    // Create a new doughnut chart for the radial progress bar
    this.chart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        datasets: [{
          data: [
            this.state.percentage, // The filled portion
            100 - this.state.percentage // The remaining portion to complete 100%
          ],
          backgroundColor: [
            this.props.color || '#4CAF50', // Use the passed color or default to green
            '#E0E0E0' // Remaining portion color
          ],
          borderColor: ['#fff', '#fff'], // Border color for segments
          borderWidth: 2,
        }]
      },
      options: {
        responsive: true,
        cutout: '80%', // Make the center empty
        rotation: -90, // Start the fill from the top
        circumference: 360, // Full circle
        plugins: {
          legend: {
            display: false, // Hide the legend
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                return `${context.raw}%`;
              }
            }
          },
          datalabels: {
            display: true,
            formatter: (value) => `${value}%`,
            color: '#000', // Text color
            font: {
              weight: 'bold',
              size: 24
            },
            align: 'center',
            anchor: 'center',
            offset: 0,
          }
        }
      }
    });
  }

  updatePercentage(newPercentage) {
    this.state.percentage = newPercentage;
    if (this.chart) {
      this.chart.data.datasets[0].data = [
        newPercentage,
        100 - newPercentage
      ];
      this.chart.update();
    }
  }
}

RadialProgressBar.template = "owl.RadialProgressBar";
