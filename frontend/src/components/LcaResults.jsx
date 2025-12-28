import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, PieChart, Pie, Cell } from 'recharts';
import { TrendingDown, Zap, Droplets, Leaf, Download } from 'lucide-react';

const LcaResults = ({ data, input }) => {
  // Prepare breakdown data for chart
  const breakdownData = [
    { name: 'Raw Material', value: data.breakdown.raw_material_extraction, color: '#ef4444' },
    { name: 'Production', value: data.breakdown.production, color: '#f59e0b' },
    { name: 'Transport', value: data.breakdown.transport, color: '#3b82f6' },
    { name: 'End of Life', value: data.breakdown.end_of_life, color: '#10b981' },
  ];

  const COLORS = ['#ef4444', '#f59e0b', '#3b82f6', '#10b981'];

  // Format numbers
  const formatNumber = (num) => {
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: 2,
      maximumFractionDigits: 2,
    }).format(num);
  };

  return (
    <div className="space-y-8">
      {/* Header with Key Metrics */}
      <div>
        <h3 className="text-2xl font-bold text-gray-900 mb-6">
          Life Cycle Assessment Results
        </h3>

        {/* Key Metrics Grid */}
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
          {/* Total CO2 */}
          <div className="bg-gradient-to-br from-red-50 to-orange-50 rounded-lg p-6 border border-red-100">
            <div className="flex items-center justify-between mb-2">
              <div className="w-10 h-10 bg-red-100 rounded-lg flex items-center justify-center">
                <TrendingDown className="w-5 h-5 text-red-600" />
              </div>
              <span className="text-xs font-medium text-red-600 bg-red-100 px-2 py-1 rounded">
                Total
              </span>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">
              {formatNumber(data.total_co2_emissions)}
            </div>
            <div className="text-sm text-gray-600">kg CO₂ Emissions</div>
            <div className="text-xs text-gray-500 mt-2">
              {formatNumber(data.co2_per_unit)} kg CO₂/kg material
            </div>
          </div>

          {/* Energy Consumption */}
          <div className="bg-gradient-to-br from-yellow-50 to-orange-50 rounded-lg p-6 border border-yellow-100">
            <div className="flex items-center justify-between mb-2">
              <div className="w-10 h-10 bg-yellow-100 rounded-lg flex items-center justify-center">
                <Zap className="w-5 h-5 text-yellow-600" />
              </div>
              <span className="text-xs font-medium text-yellow-600 bg-yellow-100 px-2 py-1 rounded">
                Energy
              </span>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">
              {formatNumber(data.energy_consumption)}
            </div>
            <div className="text-sm text-gray-600">MJ Total Energy</div>
            <div className="text-xs text-gray-500 mt-2">
              {formatNumber(data.energy_per_unit)} MJ/kg material
            </div>
          </div>

          {/* Water Usage */}
          <div className="bg-gradient-to-br from-blue-50 to-cyan-50 rounded-lg p-6 border border-blue-100">
            <div className="flex items-center justify-between mb-2">
              <div className="w-10 h-10 bg-blue-100 rounded-lg flex items-center justify-center">
                <Droplets className="w-5 h-5 text-blue-600" />
              </div>
              <span className="text-xs font-medium text-blue-600 bg-blue-100 px-2 py-1 rounded">
                Water
              </span>
            </div>
            <div className="text-3xl font-bold text-gray-900 mb-1">
              {formatNumber(data.water_usage)}
            </div>
            <div className="text-sm text-gray-600">Liters Used</div>
            <div className="text-xs text-gray-500 mt-2">
              {formatNumber(data.water_per_unit)} L/kg material
            </div>
          </div>

          {/* Carbon Savings */}
          {data.carbon_savings && (
            <div className="bg-gradient-to-br from-green-50 to-emerald-50 rounded-lg p-6 border border-green-100">
              <div className="flex items-center justify-between mb-2">
                <div className="w-10 h-10 bg-green-100 rounded-lg flex items-center justify-center">
                  <Leaf className="w-5 h-5 text-green-600" />
                </div>
                <span className="text-xs font-medium text-green-600 bg-green-100 px-2 py-1 rounded">
                  Saved
                </span>
              </div>
              <div className="text-3xl font-bold text-gray-900 mb-1">
                {formatNumber(data.carbon_savings)}
              </div>
              <div className="text-sm text-gray-600">kg CO₂ Saved</div>
              <div className="text-xs text-gray-500 mt-2">
                vs. 100% virgin material
              </div>
            </div>
          )}
        </div>
      </div>

      {/* Charts Section */}
      <div className="grid lg:grid-cols-2 gap-6">
        {/* Bar Chart - Emissions Breakdown */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">
            Emissions Breakdown by Lifecycle Stage
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <BarChart data={breakdownData}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey="name" />
              <YAxis />
              <Tooltip 
                formatter={(value) => [`${formatNumber(value)} kg CO₂`, 'Emissions']}
              />
              <Bar dataKey="value" fill="#3b82f6" radius={[8, 8, 0, 0]} />
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Pie Chart - Percentage Distribution */}
        <div className="bg-white border border-gray-200 rounded-lg p-6">
          <h4 className="text-lg font-semibold text-gray-900 mb-4">
            Emissions Distribution (%)
          </h4>
          <ResponsiveContainer width="100%" height={300}>
            <PieChart>
              <Pie
                data={breakdownData}
                cx="50%"
                cy="50%"
                labelLine={false}
                label={({ name, percent }) => `${name}: ${(percent * 100).toFixed(1)}%`}
                outerRadius={80}
                fill="#8884d8"
                dataKey="value"
              >
                {breakdownData.map((entry, index) => (
                  <Cell key={`cell-${index}`} fill={COLORS[index % COLORS.length]} />
                ))}
              </Pie>
              <Tooltip formatter={(value) => `${formatNumber(value)} kg CO₂`} />
            </PieChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Detailed Breakdown Table */}
      <div className="bg-white border border-gray-200 rounded-lg overflow-hidden">
        <div className="px-6 py-4 bg-gray-50 border-b border-gray-200">
          <h4 className="text-lg font-semibold text-gray-900">
            Detailed Breakdown
          </h4>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Lifecycle Stage
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  CO₂ Emissions (kg)
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Percentage
                </th>
                <th className="px-6 py-3 text-right text-xs font-medium text-gray-500 uppercase tracking-wider">
                  Per Unit (kg CO₂/kg)
                </th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {breakdownData.map((item, index) => {
                const percentage = (item.value / data.total_co2_emissions) * 100;
                const perUnit = item.value / input.quantity;
                return (
                  <tr key={index} className="hover:bg-gray-50">
                    <td className="px-6 py-4 whitespace-nowrap">
                      <div className="flex items-center">
                        <div
                          className="w-3 h-3 rounded-full mr-3"
                          style={{ backgroundColor: item.color }}
                        />
                        <span className="text-sm font-medium text-gray-900">
                          {item.name}
                        </span>
                      </div>
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                      {formatNumber(item.value)}
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                      {percentage.toFixed(1)}%
                    </td>
                    <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-500">
                      {formatNumber(perUnit)}
                    </td>
                  </tr>
                );
              })}
              <tr className="bg-gray-50 font-semibold">
                <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">
                  Total
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                  {formatNumber(data.total_co2_emissions)}
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                  100.0%
                </td>
                <td className="px-6 py-4 whitespace-nowrap text-right text-sm text-gray-900">
                  {formatNumber(data.co2_per_unit)}
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      {/* Input Summary */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
        <h4 className="text-lg font-semibold text-gray-900 mb-4">
          Input Summary
        </h4>
        <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-4 text-sm">
          <div>
            <span className="text-gray-600">Material:</span>
            <span className="ml-2 font-medium text-gray-900">
              {input.material.charAt(0).toUpperCase() + input.material.slice(1)}
            </span>
          </div>
          <div>
            <span className="text-gray-600">Production:</span>
            <span className="ml-2 font-medium text-gray-900">
              {input.production_type.charAt(0).toUpperCase() + input.production_type.slice(1)}
            </span>
          </div>
          <div>
            <span className="text-gray-600">Quantity:</span>
            <span className="ml-2 font-medium text-gray-900">
              {formatNumber(input.quantity)} kg
            </span>
          </div>
          <div>
            <span className="text-gray-600">Energy Source:</span>
            <span className="ml-2 font-medium text-gray-900">
              {input.energy_source.replace('_', ' ').split(' ').map(w => 
                w.charAt(0).toUpperCase() + w.slice(1)
              ).join(' ')}
            </span>
          </div>
          <div>
            <span className="text-gray-600">Transport:</span>
            <span className="ml-2 font-medium text-gray-900">
              {formatNumber(input.transport_distance)} km ({input.transport_mode})
            </span>
          </div>
          <div>
            <span className="text-gray-600">Recycled Content:</span>
            <span className="ml-2 font-medium text-gray-900">
              {input.recycled_content}%
            </span>
          </div>
          <div>
            <span className="text-gray-600">EOL Recycling:</span>
            <span className="ml-2 font-medium text-gray-900">
              {input.end_of_life_recycling_rate}%
            </span>
          </div>
        </div>
      </div>

      {/* Export Button */}
      <div className="flex justify-end">
        <button
          onClick={() => {
            // In a real app, this would trigger report generation
            alert('Report generation coming soon!');
          }}
          className="inline-flex items-center gap-2 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-colors"
        >
          <Download className="w-5 h-5" />
          Export Report (PDF)
        </button>
      </div>
    </div>
  );
};

export default LcaResults;