import { TrendingDown, TrendingUp } from 'lucide-react';

const ComparisonView = ({ current, industry }) => {
  const metrics = [
    {
      name: 'CO₂ Emissions',
      current: current.total_co2_emissions,
      industry: industry.co2_average,
      unit: 'kg CO₂',
      better: 'lower'
    },
    {
      name: 'Energy Use',
      current: current.energy_consumption,
      industry: industry.energy_average,
      unit: 'MJ',
      better: 'lower'
    },
    {
      name: 'Water Usage',
      current: current.water_usage,
      industry: industry.water_average,
      unit: 'liters',
      better: 'lower'
    }
  ];

  const getComparison = (current, industry, better) => {
    const diff = ((current - industry) / industry) * 100;
    const isBetter = better === 'lower' ? current < industry : current > industry;
    
    return {
      diff: Math.abs(diff).toFixed(1),
      isBetter,
      text: isBetter ? 'Better than industry' : 'Above industry average'
    };
  };

  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Industry Comparison
      </h3>

      <div className="space-y-4">
        {metrics.map((metric, idx) => {
          const comparison = getComparison(metric.current, metric.industry, metric.better);
          
          return (
            <div key={idx} className="border-b border-gray-200 pb-4 last:border-0">
              <div className="flex items-center justify-between mb-2">
                <span className="text-sm font-medium text-gray-700">
                  {metric.name}
                </span>
                <div className={`flex items-center gap-1 text-sm ${
                  comparison.isBetter ? 'text-green-600' : 'text-red-600'
                }`}>
                  {comparison.isBetter ? (
                    <TrendingDown className="w-4 h-4" />
                  ) : (
                    <TrendingUp className="w-4 h-4" />
                  )}
                  {comparison.diff}%
                </div>
              </div>
              
              <div className="flex items-center gap-4 text-sm">
                <div>
                  <span className="text-gray-500">You: </span>
                  <span className="font-semibold text-gray-900">
                    {metric.current.toFixed(2)} {metric.unit}
                  </span>
                </div>
                <div>
                  <span className="text-gray-500">Industry: </span>
                  <span className="font-semibold text-gray-900">
                    {metric.industry.toFixed(2)} {metric.unit}
                  </span>
                </div>
              </div>
              
              <div className={`text-xs mt-2 ${
                comparison.isBetter ? 'text-green-600' : 'text-red-600'
              }`}>
                {comparison.text}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default ComparisonView;