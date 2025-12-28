/**
 * Utility functions for formatting data
 */

// ============================================
// Number Formatting
// ============================================

/**
 * Format number with commas and decimal places
 */
export const formatNumber = (num, decimals = 2) => {
    if (num === null || num === undefined) return '-';
    
    return new Intl.NumberFormat('en-US', {
      minimumFractionDigits: decimals,
      maximumFractionDigits: decimals,
    }).format(num);
  };
  
  /**
   * Format number as percentage
   */
  export const formatPercentage = (num, decimals = 1) => {
    if (num === null || num === undefined) return '-';
    
    return `${formatNumber(num, decimals)}%`;
  };
  
  /**
   * Format large numbers with K, M, B suffixes
   */
  export const formatCompactNumber = (num) => {
    if (num === null || num === undefined) return '-';
    
    const absNum = Math.abs(num);
    
    if (absNum >= 1e9) {
      return `${(num / 1e9).toFixed(2)}B`;
    }
    if (absNum >= 1e6) {
      return `${(num / 1e6).toFixed(2)}M`;
    }
    if (absNum >= 1e3) {
      return `${(num / 1e3).toFixed(2)}K`;
    }
    
    return formatNumber(num, 2);
  };
  
  /**
   * Format currency
   */
  export const formatCurrency = (num, currency = 'USD') => {
    if (num === null || num === undefined) return '-';
    
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: currency,
    }).format(num);
  };
  
  // ============================================
  // Date & Time Formatting
  // ============================================
  
  /**
   * Format date string
   */
  export const formatDate = (dateString, options = {}) => {
    if (!dateString) return '-';
    
    const defaultOptions = {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      ...options,
    };
    
    return new Date(dateString).toLocaleDateString('en-US', defaultOptions);
  };
  
  /**
   * Format datetime string
   */
  export const formatDateTime = (dateString) => {
    if (!dateString) return '-';
    
    return new Date(dateString).toLocaleString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit',
    });
  };
  
  /**
   * Get relative time (e.g., "2 hours ago")
   */
  export const formatRelativeTime = (dateString) => {
    if (!dateString) return '-';
    
    const date = new Date(dateString);
    const now = new Date();
    const diffInSeconds = Math.floor((now - date) / 1000);
    
    if (diffInSeconds < 60) return 'just now';
    if (diffInSeconds < 3600) return `${Math.floor(diffInSeconds / 60)} minutes ago`;
    if (diffInSeconds < 86400) return `${Math.floor(diffInSeconds / 3600)} hours ago`;
    if (diffInSeconds < 604800) return `${Math.floor(diffInSeconds / 86400)} days ago`;
    
    return formatDate(dateString);
  };
  
  // ============================================
  // Text Formatting
  // ============================================
  
  /**
   * Capitalize first letter
   */
  export const capitalize = (str) => {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
  };
  
  /**
   * Convert to title case
   */
  export const toTitleCase = (str) => {
    if (!str) return '';
    return str.replace(/\w\S*/g, (txt) => 
      txt.charAt(0).toUpperCase() + txt.substr(1).toLowerCase()
    );
  };
  
  /**
   * Convert snake_case to Title Case
   */
  export const snakeToTitle = (str) => {
    if (!str) return '';
    return str
      .split('_')
      .map(word => capitalize(word))
      .join(' ');
  };
  
  /**
   * Truncate text with ellipsis
   */
  export const truncate = (str, maxLength = 50) => {
    if (!str || str.length <= maxLength) return str;
    return `${str.slice(0, maxLength)}...`;
  };
  
  // ============================================
  // Unit Conversions
  // ============================================
  
  /**
   * Convert kg to tons
   */
  export const kgToTons = (kg) => {
    return kg / 1000;
  };
  
  /**
   * Convert MJ to kWh
   */
  export const mjToKwh = (mj) => {
    return mj / 3.6;
  };
  
  /**
   * Convert kg CO2 to tons CO2
   */
  export const kgCO2ToTons = (kg) => {
    return kg / 1000;
  };
  
  // ============================================
  // Data Validation
  // ============================================
  
  /**
   * Check if value is valid number
   */
  export const isValidNumber = (value) => {
    return value !== null && value !== undefined && !isNaN(value) && isFinite(value);
  };
  
  /**
   * Clamp number between min and max
   */
  export const clamp = (num, min, max) => {
    return Math.min(Math.max(num, min), max);
  };
  
  // ============================================
  // Chart Data Formatting
  // ============================================
  
  /**
   * Format chart tooltip value
   */
  export const formatChartValue = (value, unit = '') => {
    return `${formatNumber(value)} ${unit}`.trim();
  };
  
  /**
   * Get color by value range
   */
  export const getColorByValue = (value, thresholds = { low: 30, medium: 70 }) => {
    if (value < thresholds.low) return '#10b981'; // green
    if (value < thresholds.medium) return '#f59e0b'; // yellow
    return '#ef4444'; // red
  };
  
  /**
   * Get circularity level color
   */
  export const getCircularityColor = (mciScore) => {
    if (mciScore >= 0.9) return '#10b981'; // Excellent - Green
    if (mciScore >= 0.7) return '#22c55e'; // High - Light Green
    if (mciScore >= 0.5) return '#f59e0b'; // Medium - Yellow
    if (mciScore >= 0.3) return '#f97316'; // Low - Orange
    return '#ef4444'; // Very Low - Red
  };
  
  /**
   * Get impact level color
   */
  export const getImpactColor = (impact) => {
    const colors = {
      'High': '#ef4444',
      'Medium': '#f59e0b',
      'Low': '#10b981',
    };
    return colors[impact] || '#6b7280';
  };
  
  /**
   * Get difficulty color
   */
  export const getDifficultyColor = (difficulty) => {
    const colors = {
      'Easy': '#10b981',
      'Medium': '#f59e0b',
      'Hard': '#ef4444',
    };
    return colors[difficulty] || '#6b7280';
  };
  
  // ============================================
  // File Size Formatting
  // ============================================
  
  /**
   * Format bytes to human readable size
   */
  export const formatFileSize = (bytes) => {
    if (bytes === 0) return '0 Bytes';
    
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    
    return `${parseFloat((bytes / Math.pow(k, i)).toFixed(2))} ${sizes[i]}`;
  };
  
  // ============================================
  // Export Default Object
  // ============================================
  
  export default {
    formatNumber,
    formatPercentage,
    formatCompactNumber,
    formatCurrency,
    formatDate,
    formatDateTime,
    formatRelativeTime,
    capitalize,
    toTitleCase,
    snakeToTitle,
    truncate,
    kgToTons,
    mjToKwh,
    kgCO2ToTons,
    isValidNumber,
    clamp,
    formatChartValue,
    getColorByValue,
    getCircularityColor,
    getImpactColor,
    getDifficultyColor,
    formatFileSize,
  };