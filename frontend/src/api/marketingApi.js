import axios from 'axios';

const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000/api';

const api = axios.create({
  baseURL: API_BASE_URL,
  timeout: 10000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Executive endpoints
export const getExecutiveSummary = (days = 30) => 
  api.get(`/executive/summary?days=${days}`);

export const getExecutiveTrends = (days = 30) => 
  api.get(`/executive/trends?days=${days}`);

// Paid media endpoints
export const getPaidChannels = (days = 30) => 
  api.get(`/paid/channels?days=${days}`);

export const getPaidCampaigns = (days = 30, channel = null) => {
  const url = channel 
    ? `/paid/campaigns?days=${days}&channel=${channel}`
    : `/paid/campaigns?days=${days}`;
  return api.get(url);
};

// Organic endpoints
export const getOrganicSummary = (days = 30) => 
  api.get(`/organic/summary?days=${days}`);

export const getOrganicTrends = (days = 30) => 
  api.get(`/organic/trends?days=${days}`);

// Signals endpoints
export const getSignals = (days = 7, severity = 'all') => 
  api.get(`/signals?days=${days}&severity=${severity}`);

export const dismissSignal = (signalId) => 
  api.post(`/signals/${signalId}/dismiss`);

// Scenario endpoints
export const predictScenario = (scenarioData) => 
  api.post('/scenarios/predict', scenarioData);

// Health check
export const healthCheck = () => 
  api.get('/health');

export default api;
