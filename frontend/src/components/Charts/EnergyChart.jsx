import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const EnergyChart = ({ data }) => {
  const chartData = [
    {
      stage: 'Extraction',
      energy: data.breakdown.raw_material_extraction * 0.3,
    },
    {
      stage: 'Production',
      energy: data.energy_consumption * 0.6,
    },
    {
      stage: 'Transport',
      energy: data.breakdown.transport * 0.5,
    },
    {
      stage: 'EOL',
      energy: data.breakdown.end_of_life * 0.2,
    },
  ];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Energy Consumption Profile
      </h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" />
          <XAxis dataKey="stage" />
          <YAxis />
          <Tooltip formatter={(value) => `${value.toFixed(2)} MJ`} />
          <Legend />
          <Line 
            type="monotone" 
            dataKey="energy" 
            stroke="#f59e0b" 
            strokeWidth={2}
            name="Energy (MJ)"
          />
        </LineChart>
      </ResponsiveContainer>
    </div>
  );
};

export default EnergyChart;