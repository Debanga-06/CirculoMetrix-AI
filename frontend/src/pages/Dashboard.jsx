import { useState } from 'react';
import { toast } from 'react-hot-toast';
import axios from 'axios';

// Components
import InputForm from '../components/InputForm';
import LcaResults from '../components/LcaResults';
import { Loader2 } from 'lucide-react';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

const Dashboard = () => {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [activeTab, setActiveTab] = useState('lca'); // lca, circularity, recommendations

  const handleCalculate = async (formData) => {
    setLoading(true);
    setResults(null);

    try {
      // Calculate LCA
      const lcaResponse = await axios.post(
        `${API_BASE_URL}/api/v1/lca/calculate`,
        formData
      );

      // Calculate Circularity
      const circularityInput = {
        material: formData.material,
        virgin_material_input: formData.quantity * (1 - formData.recycled_content / 100),
        recycled_material_input: formData.quantity * (formData.recycled_content / 100),
        waste_generated: formData.quantity * 0.1,
        waste_recycled: formData.quantity * 0.1 * (formData.end_of_life_recycling_rate / 100),
        product_lifespan: 20
      };

      const circularityResponse = await axios.post(
        `${API_BASE_URL}/api/v1/circularity/calculate`,
        circularityInput
      );

      // Get Recommendations
      const recommendationsResponse = await axios.post(
        `${API_BASE_URL}/api/v1/recommendations/generate`,
        formData,
        { params: { include_circularity: true } }
      );

      // Get AI Prediction
      const aiInput = {
        material: formData.material,
        production_volume: formData.quantity,
        energy_source: formData.energy_source,
        recycled_content: formData.recycled_content,
        process_efficiency: 85
      };

      const aiResponse = await axios.post(
        `${API_BASE_URL}/api/v1/ai/predict`,
        aiInput
      );
      console.log('AI Prediction response data:', aiResponse.data.data);


      setResults({
        lca: lcaResponse.data.data,
        circularity: circularityResponse.data.data,
        recommendations: recommendationsResponse.data.data,
        ai_prediction: aiResponse.data.data,
        input: formData
      });

      toast.success('Analysis completed successfully!');
      setActiveTab('lca');
    } catch (error) {
      console.error('Error calculating LCA:', error);
      toast.error(
        error.response?.data?.detail || 'Failed to calculate. Please try again.'
      );
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-8">
      {/* Header */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h1 className="text-3xl font-bold text-gray-900 mb-2">
          LCA Dashboard
        </h1>
        <p className="text-gray-600">
          Calculate environmental impact and get sustainability recommendations
        </p>
      </div>

      {/* Input Form */}
      <div className="bg-white rounded-lg shadow-sm p-6">
        <h2 className="text-xl font-semibold text-gray-900 mb-6">
          Input Parameters
        </h2>
        <InputForm onSubmit={handleCalculate} loading={loading} />
      </div>

      {/* Loading State */}
      {loading && (
        <div className="bg-white rounded-lg shadow-sm p-12">
          <div className="flex flex-col items-center justify-center space-y-4">
            <Loader2 className="w-12 h-12 text-blue-600 animate-spin" />
            <p className="text-gray-600 text-lg">
              Analyzing your data...
            </p>
            <p className="text-gray-500 text-sm">
              This may take a few seconds
            </p>
          </div>
        </div>
      )}

      {/* Results */}
      {results && !loading && (
        <div className="space-y-6">
          {/* Tabs */}
          <div className="bg-white rounded-lg shadow-sm">
            <div className="border-b border-gray-200">
              <nav className="flex space-x-8 px-6" aria-label="Tabs">
                <button
                  onClick={() => setActiveTab('lca')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'lca'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                >
                  LCA Results
                </button>
                <button
                  onClick={() => setActiveTab('circularity')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'circularity'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                >
                  Circularity Metrics
                </button>
                <button
                  onClick={() => setActiveTab('recommendations')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'recommendations'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                >
                  Recommendations
                </button>
                <button
                  onClick={() => setActiveTab('ai')}
                  className={`py-4 px-1 border-b-2 font-medium text-sm ${activeTab === 'ai'
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                    }`}
                >
                  AI Insights
                </button>
              </nav>
            </div>

            {/* Tab Content */}
            <div className="p-6">
              {activeTab === 'lca' && (
                <LcaResults data={results.lca} input={results.input} />
              )}

              {activeTab === 'circularity' && (
                <div className="space-y-6">
                  <h3 className="text-2xl font-bold text-gray-900">
                    Circular Economy Metrics
                  </h3>

                  {/* MCI Score */}
                  <div className="bg-gradient-to-r from-green-50 to-blue-50 rounded-lg p-6">
                    <div className="flex items-center justify-between">
                      <div>
                        <div className="text-sm text-gray-600 mb-1">
                          Material Circularity Indicator (MCI)
                        </div>
                        <div className="text-5xl font-bold text-gray-900">
                          {results.circularity.mci_score.toFixed(3)}
                        </div>
                        <div className="text-lg text-gray-600 mt-2">
                          Circularity Level: <span className="font-semibold text-blue-600">
                            {results.circularity.circularity_level}
                          </span>
                        </div>
                      </div>
                      <div className="text-6xl">
                        {results.circularity.mci_score >= 0.7 ? '🌟' :
                          results.circularity.mci_score >= 0.5 ? '✨' : '📊'}
                      </div>
                    </div>
                  </div>

                  {/* Metrics Grid */}
                  <div className="grid md:grid-cols-3 gap-6">
                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                      <div className="text-sm text-gray-600 mb-2">
                        Recycled Content Rate
                      </div>
                      <div className="text-3xl font-bold text-gray-900">
                        {results.circularity.recycled_content_rate.toFixed(1)}%
                      </div>
                    </div>

                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                      <div className="text-sm text-gray-600 mb-2">
                        EOL Recycling Rate
                      </div>
                      <div className="text-3xl font-bold text-gray-900">
                        {results.circularity.end_of_life_recycling_rate.toFixed(1)}%
                      </div>
                    </div>

                    <div className="bg-white border border-gray-200 rounded-lg p-6">
                      <div className="text-sm text-gray-600 mb-2">
                        Waste Reduction
                      </div>
                      <div className="text-3xl font-bold text-gray-900">
                        {results.circularity.waste_reduction.toFixed(1)}%
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {activeTab === 'recommendations' && (
                <div className="space-y-6">
                  <h3 className="text-2xl font-bold text-gray-900">
                    Sustainability Recommendations
                  </h3>

                  {/* Priority Actions */}
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                    <h4 className="font-semibold text-blue-900 mb-3">
                      Priority Actions
                    </h4>
                    <ul className="space-y-2">
                      {results.recommendations.priority_actions.map((action, idx) => (
                        <li key={idx} className="flex items-start gap-2 text-blue-800">
                          <span className="font-bold">{idx + 1}.</span>
                          <span>{action}</span>
                        </li>
                      ))}
                    </ul>
                  </div>

                  {/* Recommendations List */}
                  <div className="space-y-4">
                    {results.recommendations.recommendations.map((rec, idx) => (
                      <div
                        key={idx}
                        className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow"
                      >
                        <div className="flex items-start justify-between mb-3">
                          <h4 className="text-lg font-semibold text-gray-900">
                            {rec.title}
                          </h4>
                          <div className="flex gap-2">
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${rec.impact === 'High'
                              ? 'bg-red-100 text-red-800'
                              : rec.impact === 'Medium'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-green-100 text-green-800'
                              }`}>
                              {rec.impact} Impact
                            </span>
                            <span className={`px-3 py-1 rounded-full text-xs font-medium ${rec.implementation_difficulty === 'Easy'
                              ? 'bg-green-100 text-green-800'
                              : rec.implementation_difficulty === 'Medium'
                                ? 'bg-yellow-100 text-yellow-800'
                                : 'bg-red-100 text-red-800'
                              }`}>
                              {rec.implementation_difficulty}
                            </span>
                          </div>
                        </div>
                        <p className="text-gray-600 mb-4">
                          {rec.description}
                        </p>
                        <div className="flex items-center gap-6 text-sm">
                          <div>
                            <span className="text-gray-500">Category:</span>
                            <span className="ml-2 font-medium text-gray-900">
                              {rec.category}
                            </span>
                          </div>
                          {rec.estimated_savings.co2_reduction && (
                            <div>
                              <span className="text-gray-500">CO₂ Savings:</span>
                              <span className="ml-2 font-medium text-green-600">
                                {rec.estimated_savings.co2_reduction.toFixed(2)} kg
                              </span>
                            </div>
                          )}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {activeTab === 'ai' && (
                <div className="space-y-6">
                  <h3 className="text-2xl font-bold text-gray-900">
                    AI Predictions & Insights
                  </h3>

                  <div className="grid md:grid-cols-2 gap-6">
                    <div className="bg-gradient-to-br from-purple-50 to-blue-50 rounded-lg p-6">
                      <div className="text-sm text-gray-600 mb-2">
                        Predicted CO₂ Emissions
                      </div>
                      <div className="text-4xl font-bold text-gray-900 mb-2">
                        {results.ai_prediction.predicted_co2_emissions.toFixed(2)}
                      </div>
                      <div className="text-sm text-gray-600">
                        kg CO₂
                      </div>
                    </div>

                    <div className="bg-gradient-to-br from-blue-50 to-green-50 rounded-lg p-6">
                      <div className="text-sm text-gray-600 mb-2">
                        Predicted Energy Consumption
                      </div>
                      <div className="text-4xl font-bold text-gray-900 mb-2">
                        {results.ai_prediction.predicted_energy_consumption.toFixed(2)}
                      </div>
                      <div className="text-sm text-gray-600">
                        MJ
                      </div>
                    </div>
                  </div>

                  <div className="bg-white border border-gray-200 rounded-lg p-6">
                    <div className="flex items-center justify-between mb-4">
                      <h4 className="font-semibold text-gray-900">
                        Prediction Confidence
                      </h4>
                      <span className="text-2xl font-bold text-blue-600">
                        {(results.ai_prediction.confidence_score * 100).toFixed(1)}%
                      </span>
                    </div>
                    <div className="w-full bg-gray-200 rounded-full h-3">
                      <div
                        className="bg-blue-600 h-3 rounded-full transition-all"
                        style={{ width: `${results.ai_prediction.confidence_score * 100}%` }}
                      />
                    </div>
                  </div>

                  <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
                    <h4 className="font-semibold text-yellow-900 mb-3">
                      Prediction Range
                    </h4>

                    <div className="grid grid-cols-2 gap-4 text-sm">
                      {/* CO₂ Range */}
                      <div>
                        <div className="text-yellow-700">CO₂ Range:</div>
                        <div className="font-medium text-yellow-900">
                          {results.ai_prediction?.prediction_range?.min?.toFixed(2)} -{' '}
                          {results.ai_prediction?.prediction_range?.max?.toFixed(2)} kg
                        </div>
                      </div>

                      {/* Energy Range (Estimated) */}
                      <div>
                        <div className="text-yellow-700">Energy Range:</div>
                        <div className="font-medium text-yellow-900">
                          {(results.ai_prediction.predicted_energy_consumption * 0.85).toFixed(2)} -{' '}
                          {(results.ai_prediction.predicted_energy_consumption * 1.15).toFixed(2)} MJ
                        </div>
                      </div>
                    </div>
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default Dashboard;