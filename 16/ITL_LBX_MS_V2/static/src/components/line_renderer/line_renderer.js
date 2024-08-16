/** @odoo-module */

import { registry } from "@web/core/registry";
import { loadJS } from "@web/core/assets";
const { Component, useRef, onMounted } = owl;

export class RadialProgressBar extends Component {
  setup() {
    this.chartRef = useRef('chart');

    onMounted(() => this.renderChart());
  }

  async renderChart() {
    // Load Chart.js if not already loaded
    await loadJS('https://cdnjs.cloudflare.com/ajax/libs/Chart.js/4.4.0/chart.umd.min.js');

    // Ensure Chart.js is available
    if (!window.Chart) {
      console.error('Chart.js is not loaded');
      return;
    }

    // Get the canvas context
    const ctx = this.chartRef.el.getContext('2d');

    // Create a new doughnut chart for the radial progress bar
    new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: ['Progress'],  // Single label for the progress
        datasets: [{
          data: [70, 30],  // 70% completion, 30% remaining
          backgroundColor: ['#36A2EB', '#E0E0E0'],  // Color for completed and remaining segments
          borderColor: ['#fff', '#fff'],  // Border color for segments
          borderWidth: 2,
        }]
      },
      options: {
        responsive: true,
        cutout: '80%',  // Make the center empty
        rotation: -90,  // Start the fill from the top
        circumference: 360,  // Full circle
        plugins: {
          legend: {
            display: false,  // Hide the legend
          },
          tooltip: {
            callbacks: {
              label: function (context) {
                const percentage = context.raw[0];
                return `${percentage}%`;
              }
            }
          },
          datalabels: {
            display: true,
            formatter: (value) => `${value}%`,
            color: '#36A2EB',
            font: {
              weight: 'bold',
              size: 20,
            }
          }
        }
      }
    });
  }
}

RadialProgressBar.template = "owl.RadialProgressBar";
