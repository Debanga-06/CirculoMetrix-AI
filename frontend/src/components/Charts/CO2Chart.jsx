import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const CO2Chart = ({ data }) => {
  const chartData = [
    {
      name: 'Raw Material',
      co2: data.breakdown.raw_material_extraction,
    },
    {
      name: 'Production',
      co2: data.breakdown.production,
    },
    {
      name: 'Transport',
      co2: data.breakdown.transport,
    },
    {
      name: 'End of Life',
      co2: data.breakdown.end_of_life,
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        CO₂ Emissions by Lifecycle Stage
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <BarChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="name" />
          <YAxis />
          <Tooltip formatter={(value) => `${value.toFixed(2)} kg CO₂`} />
          <Legend />
          <Bar dataKey="co2" fill="#3b82f6" name="CO₂ Emissions (kg)" />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
};

export default CO2Chart;