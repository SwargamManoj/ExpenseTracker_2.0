import React from "react";
import { Bar } from "react-chartjs-2";

const ExpenseCategoryChart = ({ data, totalExpenses }) => {
  const labels = data.map((item) => item.category);
  const amounts = data.map((item) => item.total_amount);

  const chartData = {
    labels: labels,
    datasets: [
      {
        label: "Expenses by Category",
        data: amounts,
        backgroundColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4BC0C0",
          "#9966FF",
          "#FF9F40",
        ],
        borderColor: [
          "#FF6384",
          "#36A2EB",
          "#FFCE56",
          "#4BC0C0",
          "#9966FF",
          "#FF9F40",
        ],
        borderWidth: 1,
      },
    ],
  };

  const options = {
    responsive: true,
    plugins: {
      legend: {
        position: "top",
      },
    },
    scales: {
      y: {
        beginAtZero: true,
      },
    },
  };

  return (
    <div>
      <h4>Total Expenses: ${totalExpenses.toFixed(2)}</h4>
      <Bar data={chartData} options={options} />
    </div>
  );
};

export default ExpenseCategoryChart;
