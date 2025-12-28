import axios from 'axios';

// Base API URL from environment variables
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000';

// Create axios instance with default config
const api = axios.create({
  baseURL: API_BASE_URL,
  headers: {
    'Content-Type': 'application/json',
  },
  timeout: 30000, // 30 seconds
});

// Request interceptor
api.interceptors.request.use(
  (config) => {
    // Add auth token if available
    const token = localStorage.getItem('access_token');
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => {
    return Promise.reject(error);
  }
);

// Response interceptor
api.interceptors.response.use(
  (response) => {
    return response;
  },
  (error) => {
    // Handle errors globally
    if (error.response) {
      // Server responded with error
      console.error('API Error:', error.response.data);
      
      // Handle 401 Unauthorized
      if (error.response.status === 401) {
        localStorage.removeItem('access_token');
        // Redirect to login if needed
      }
    } else if (error.request) {
      // Request made but no response
      console.error('Network Error:', error.message);
    } else {
      // Something else happened
      console.error('Error:', error.message);
    }
    
    return Promise.reject(error);
  }
);

// ============================================
// LCA Endpoints
// ============================================

export const lcaAPI = {
  // Calculate LCA
  calculate: (data) => api.post('/api/v1/lca/calculate', data),
  
  // Compare scenarios
  compare: (baseScenario, altScenario) => 
    api.post('/api/v1/lca/compare', { baseScenario, altScenario }),
  
  // Get emission factors
  getEmissionFactors: () => api.get('/api/v1/lca/emission-factors'),
  
  // Get transport factors
  getTransportFactors: () => api.get('/api/v1/lca/transport-factors'),
  
  // Batch calculate
  batchCalculate: (inputs) => api.post('/api/v1/lca/batch-calculate', inputs),
  
  // Get typical breakdown
  getTypicalBreakdown: (material, productionType) => 
    api.get(`/api/v1/lca/breakdown/${material}/${productionType}`),
  
  // Calculate carbon savings
  calculateCarbonSavings: (current, targetRecycledContent) =>
    api.post('/api/v1/lca/carbon-savings', current, {
      params: { target_recycled_content: targetRecycledContent }
    }),
  
  // Get industry benchmarks
  getBenchmarks: (material) => api.get(`/api/v1/lca/benchmarks/${material}`),
};

// ============================================
// Circularity Endpoints
// ============================================

export const circularityAPI = {
  // Calculate circularity metrics
  calculate: (data) => api.post('/api/v1/circularity/calculate', data),
  
  // Material flow analysis
  materialFlow: (data) => api.post('/api/v1/circularity/material-flow', data),
  
  // Generate Sankey diagram data
  generateSankey: (data) => api.post('/api/v1/circularity/sankey', data),
  
  // Benchmark circularity
  benchmark: (data) => api.post('/api/v1/circularity/benchmark', data),
  
  // Gap analysis
  gapAnalysis: (data, targetMCI = 0.9) =>
    api.post('/api/v1/circularity/gap-analysis', data, {
      params: { target_mci: targetMCI }
    }),
  
  // Get MCI explanation
  getMCIExplanation: () => api.get('/api/v1/circularity/mci-explanation'),
  
  // Get industry averages
  getIndustryAverages: () => api.get('/api/v1/circularity/industry-averages'),
  
  // Calculate improvement potential
  improvementPotential: (data) =>
    api.post('/api/v1/circularity/improvement-potential', data),
};

// ============================================
// AI Prediction Endpoints
// ============================================

export const aiAPI = {
  // Make prediction
  predict: (data) => api.post('/api/v1/ai/predict', data),
  
  // Batch predictions
  batchPredict: (inputs) => api.post('/api/v1/ai/batch-predict', inputs),
  
  // Get model info
  getModelInfo: () => api.get('/api/v1/ai/model-info'),
  
  // Compare predictions
  comparePredictions: (scenarios) =>
    api.post('/api/v1/ai/compare-predictions', scenarios),
  
  // Sensitivity analysis
  sensitivityAnalysis: (baseInput, parameter, rangeMin, rangeMax, steps = 5) =>
    api.post('/api/v1/ai/sensitivity-analysis', baseInput, {
      params: { parameter, range_min: rangeMin, range_max: rangeMax, steps }
    }),
  
  // Get confidence factors
  getConfidenceFactors: () => api.get('/api/v1/ai/confidence-factors'),
};

// ============================================
// Recommendations Endpoints
// ============================================

export const recommendationsAPI = {
  // Generate recommendations
  generate: (lcaInput, includeCircularity = false) =>
    api.post('/api/v1/recommendations/generate', lcaInput, {
      params: { include_circularity: includeCircularity }
    }),
  
  // Filter recommendations
  filter: (lcaInput, filters = {}) =>
    api.post('/api/v1/recommendations/filter', lcaInput, { params: filters }),
  
  // Get categories
  getCategories: () => api.get('/api/v1/recommendations/categories'),
  
  // Prioritize recommendations
  prioritize: (lcaInput, priorityCriteria = 'impact') =>
    api.post('/api/v1/recommendations/prioritize', lcaInput, {
      params: { priority_criteria: priorityCriteria }
    }),
  
  // Get quick wins
  getQuickWins: (lcaInput) =>
    api.post('/api/v1/recommendations/quick-wins', lcaInput),
  
  // Generate action plan
  generateActionPlan: (lcaInput, timeframeMonths = 12) =>
    api.post('/api/v1/recommendations/action-plan', lcaInput, {
      params: { timeframe_months: timeframeMonths }
    }),
};

// ============================================
// What-If Analysis Endpoints
// ============================================

export const whatIfAPI = {
  // Analyze scenario
  analyze: (scenario) => api.post('/api/v1/what-if/analyze', scenario),
  
  // Compare multiple scenarios
  compareMultiple: (baseInput, scenarios) =>
    api.post('/api/v1/what-if/compare-multiple', { base_input: baseInput, scenarios }),
  
  // Get predefined scenarios
  getPredefined: () => api.get('/api/v1/what-if/predefined'),
  
  // Analyze predefined scenario
  analyzePredefined: (scenarioKey, baseInput) =>
    api.post(`/api/v1/what-if/predefined/${scenarioKey}`, baseInput),
  
  // Sensitivity analysis
  sensitivity: (baseInput, parameter, minValue, maxValue, steps = 5) =>
    api.post('/api/v1/what-if/sensitivity', null, {
      params: {
        base_input: JSON.stringify(baseInput),
        parameter,
        min_value: minValue,
        max_value: maxValue,
        steps
      }
    }),
  
  // Optimize parameters
  optimize: (baseInput, goal = 'minimize_co2') =>
    api.post('/api/v1/what-if/optimize', baseInput, {
      params: { goal }
    }),
  
  // Calculate target achievement
  targetAchievement: (baseInput, targetReductionPercent) =>
    api.post('/api/v1/what-if/target-achievement', baseInput, {
      params: { target_reduction_percent: targetReductionPercent }
    }),
  
  // Build custom scenario
  buildCustom: (baseInput, params = {}) =>
    api.post('/api/v1/what-if/scenario-builder', baseInput, { params }),
};

// ============================================
// Report Endpoints
// ============================================

export const reportAPI = {
  // Generate report
  generate: (reportRequest) => api.post('/api/v1/report/generate', reportRequest),
  
  // Download report
  download: (reportId) =>
    api.get(`/api/v1/report/download/${reportId}`, { responseType: 'blob' }),
  
  // Preview report
  preview: (reportId) => api.get(`/api/v1/report/preview/${reportId}`),
  
  // Delete report
  delete: (reportId) => api.delete(`/api/v1/report/delete/${reportId}`),
  
  // List reports
  list: (limit = 10) => api.get('/api/v1/report/list', { params: { limit } }),
  
  // Email report
  email: (reportId, email) =>
    api.post('/api/v1/report/email', null, {
      params: { report_id: reportId, email }
    }),
  
  // Get templates
  getTemplates: () => api.get('/api/v1/report/templates'),
};

// ============================================
// Utility Functions
// ============================================

export const utils = {
  // Check API health
  healthCheck: () => api.get('/health'),
  
  // Get API info
  getApiInfo: () => api.get('/api/info'),
};

// Export the axios instance for custom requests
export default api;