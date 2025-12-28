import { PieChart, Pie, Cell, ResponsiveContainer, Legend, Tooltip } from 'recharts';

const CircularityChart = ({ mciScore, recycledContent, eolRecycling }) => {
  const data = [
    { name: 'Recycled Content', value: recycledContent },
    { name: 'Virgin Content', value: 100 - recycledContent },
  ];

  const COLORS = ['#10b981', '#ef4444'];

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Material Composition
      </h3>
      
      <div className="text-center mb-4">
        <div className="text-5xl font-bold text-gray-900 mb-2">
          {mciScore.toFixed(3)}
        </div>
        <div className="text-sm text-gray-600">
          Material Circularity Indicator
        </div>
      </div>

      <ResponsiveContainer width="100%" height={250}>
        <PieChart>
          <Pie
            data={data}
            cx="50%"
            cy="50%"
            labelLine={false}
            label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(0)}%`}
            outerRadius={80}
            fill="#8884d8"
            dataKey="value"
          >
            {data.map((entry, index) => (
              <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
            ))}
          </Pie>
          <Tooltip />
          <Legend />
        </PieChart>
      </ResponsiveContainer>

      <div className="mt-4 text-sm text-gray-600">
        <div className="flex justify-between mb-2">
          <span>EOL Recycling Rate:</span>
          <span className="font-semibold">{eolRecycling.toFixed(1)}%</span>
        </div>
      </div>
    </div>
  );
};

export default CircularityChart;