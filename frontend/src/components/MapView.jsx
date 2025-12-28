import { MapPin } from 'lucide-react';

const MapView = ({ transportDistance, transportMode }) => {
  return (
    <div className="bg-white rounded-lg shadow p-6">
      <h3 className="text-lg font-semibold text-gray-900 mb-4">
        Transport Route
      </h3>
      
      <div className="bg-gray-100 rounded-lg p-8 text-center">
        <MapPin className="w-12 h-12 text-blue-600 mx-auto mb-4" />
        
        <div className="space-y-2">
          <div className="text-2xl font-bold text-gray-900">
            {transportDistance} km
          </div>
          <div className="text-sm text-gray-600">
            Transport Distance
          </div>
          <div className="inline-flex items-center px-3 py-1 bg-blue-100 text-blue-800 rounded-full text-sm font-medium mt-2">
            {transportMode}
          </div>
        </div>

        <p className="text-xs text-gray-500 mt-6">
          Interactive map visualization would be shown here
          <br />
          (Integration with Google Maps or Mapbox)
        </p>
      </div>
    </div>
  );
};

export default MapView;