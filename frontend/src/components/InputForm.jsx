import { useState } from 'react';
import { Calculator, Info } from 'lucide-react';

const InputForm = ({ onSubmit, loading }) => {
  const [formData, setFormData] = useState({
    material: 'aluminium',
    production_type: 'secondary',
    quantity: 1000,
    energy_source: 'grid_average',
    transport_distance: 500,
    transport_mode: 'truck',
    recycled_content: 75,
    end_of_life_recycling_rate: 80,
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData((prev) => ({
      ...prev,
      [name]: ['quantity', 'transport_distance', 'recycled_content', 'end_of_life_recycling_rate'].includes(name)
        ? parseFloat(value) || 0
        : value,
    }));
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    onSubmit(formData);
  };

  return (
    <form onSubmit={handleSubmit} className="space-y-6">
      {/* Material Selection */}
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Material Type
          </label>
          <select
            name="material"
            value={formData.material}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="aluminium">Aluminum / Aluminium</option>
            <option value="copper">Copper</option>
            <option value="steel">Steel</option>
          </select>
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Production Type
          </label>
          <select
            name="production_type"
            value={formData.production_type}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="primary">Primary (Virgin Material)</option>
            <option value="secondary">Secondary (Recycled)</option>
          </select>
        </div>
      </div>

      {/* Quantity and Energy */}
      <div className="grid md:grid-cols-2 gap-6">
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Quantity (kg)
          </label>
          <input
            type="number"
            name="quantity"
            value={formData.quantity}
            onChange={handleChange}
            min="1"
            step="0.01"
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          />
        </div>

        <div>
          <label className="block text-sm font-medium text-gray-700 mb-2">
            Energy Source
          </label>
          <select
            name="energy_source"
            value={formData.energy_source}
            onChange={handleChange}
            className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="renewable">Renewable (Solar/Wind/Hydro)</option>
            <option value="fossil">Fossil Fuels</option>
            <option value="grid_average">Grid Average</option>
            <option value="nuclear">Nuclear</option>
          </select>
        </div>
      </div>

      {/* Transport */}
      <div className="bg-gray-50 rounded-lg p-4 space-y-4">
        <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
          <Info className="w-4 h-4" />
          Transportation Details
        </h3>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Transport Distance (km)
            </label>
            <input
              type="number"
              name="transport_distance"
              value={formData.transport_distance}
              onChange={handleChange}
              min="0"
              step="1"
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Transport Mode
            </label>
            <select
              name="transport_mode"
              value={formData.transport_mode}
              onChange={handleChange}
              className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            >
              <option value="truck">Truck</option>
              <option value="rail">Rail</option>
              <option value="ship">Ship</option>
              <option value="air">Air</option>
            </select>
          </div>
        </div>
      </div>

      {/* Circularity Metrics */}
      <div className="bg-green-50 rounded-lg p-4 space-y-4">
        <h3 className="text-sm font-semibold text-gray-900 flex items-center gap-2">
          <Info className="w-4 h-4" />
          Circular Economy Parameters
        </h3>

        <div className="grid md:grid-cols-2 gap-4">
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Recycled Content (%)
            </label>
            <div className="flex items-center gap-3">
              <input
                type="range"
                name="recycled_content"
                value={formData.recycled_content}
                onChange={handleChange}
                min="0"
                max="100"
                step="5"
                className="flex-1"
              />
              <span className="text-sm font-semibold text-gray-900 w-12 text-right">
                {formData.recycled_content}%
              </span>
            </div>
          </div>

          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              End-of-Life Recycling Rate (%)
            </label>
            <div className="flex items-center gap-3">
              <input
                type="range"
                name="end_of_life_recycling_rate"
                value={formData.end_of_life_recycling_rate}
                onChange={handleChange}
                min="0"
                max="100"
                step="5"
                className="flex-1"
              />
              <span className="text-sm font-semibold text-gray-900 w-12 text-right">
                {formData.end_of_life_recycling_rate}%
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Submit Button */}
      <button
        type="submit"
        disabled={loading}
        className={`w-full py-3 px-6 rounded-lg font-semibold text-white flex items-center justify-center gap-2 transition-colors ${
          loading
            ? 'bg-gray-400 cursor-not-allowed'
            : 'bg-blue-600 hover:bg-blue-700'
        }`}
      >
        <Calculator className="w-5 h-5" />
        {loading ? 'Calculating...' : 'Calculate LCA'}
      </button>

      {/* Info Note */}
      <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
        <p className="text-sm text-blue-800">
          <strong>Note:</strong> All calculations are based on ISO 14040/14044 
          standards and industry-standard emission factors. Results are estimates 
          and should be validated by certified environmental consultants for 
          official reporting.
        </p>
      </div>
    </form>
  );
};

export default InputForm;