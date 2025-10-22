import React, { useState, useEffect } from 'react';
import { Container, Grid, Typography, Paper, Box, CircularProgress } from '@mui/material';
import { BarChart, Bar, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, Cell } from 'recharts';
import KPICard from '../components/KPICard';
import { getFunnelSummary, getFunnelTrends } from '../api/marketingApi';
import VisibilityIcon from '@mui/icons-material/Visibility';
import TouchAppIcon from '@mui/icons-material/TouchApp';
import GetAppIcon from '@mui/icons-material/GetApp';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';

function FunnelDashboard() {
  const [loading, setLoading] = useState(true);
  const [summary, setSummary] = useState(null);
  const [trends, setTrends] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [summaryRes, trendsRes] = await Promise.all([
        getFunnelSummary(30),
        getFunnelTrends(30)
      ]);
      setSummary(summaryRes.data);
      setTrends(trendsRes.data);
      setError(null);
    } catch (err) {
      console.error('Error loading data:', err);
      setError('Failed to load data. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <Box display="flex" justifyContent="center" alignItems="center" minHeight="400px">
        <CircularProgress />
      </Box>
    );
  }

  if (error) {
    return (
      <Container>
        <Paper sx={{ p: 3, mt: 2, bgcolor: 'error.light' }}>
          <Typography color="error">{error}</Typography>
        </Paper>
      </Container>
    );
  }

  // Prepare funnel visualization data
  const funnelData = [
    { 
      stage: 'Impressions', 
      value: summary?.impressions || 0, 
      percentage: 100,
      color: '#1976d2'
    },
    { 
      stage: 'Clicks', 
      value: summary?.clicks || 0, 
      percentage: summary?.impressions > 0 ? (summary.clicks / summary.impressions * 100).toFixed(2) : 0,
      color: '#42a5f5'
    },
    { 
      stage: 'Installs', 
      value: summary?.installs || 0, 
      percentage: summary?.impressions > 0 ? (summary.installs / summary.impressions * 100).toFixed(2) : 0,
      color: '#64b5f6'
    }
  ];

  // Cost per stage data
  const costData = [
    { stage: 'CPM', value: summary?.cpm || 0, label: 'Cost per 1000 impressions' },
    { stage: 'CPC', value: summary?.cpc || 0, label: 'Cost per click' },
    { stage: 'CPI', value: summary?.cpi || 0, label: 'Cost per install' }
  ];

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom sx={{ color: '#1a1a1a', fontWeight: 600 }}>
        Acquisition Funnel Analysis
      </Typography>
      <Typography variant="body1" gutterBottom sx={{ mb: 3, color: '#555555' }}>
        Complete user journey from ad impression to install - identify bottlenecks and optimize conversion rates
      </Typography>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Total Impressions"
            value={(summary?.impressions || 0).toLocaleString()}
            subtitle="Ad views"
            icon={VisibilityIcon}
            tooltip="Total number of times your ads were shown to users across all channels. This is the top of your acquisition funnel. Higher impressions = broader reach."
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Click-Through Rate"
            value={`${summary?.ctr || 0}%`}
            subtitle="Impressions → Clicks"
            icon={TouchAppIcon}
            tooltip="Percentage of people who clicked your ad after seeing it. Industry benchmark: 1-3%. Higher CTR = more engaging creative. Formula: (Clicks ÷ Impressions) × 100"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Conversion Rate"
            value={`${summary?.cvr || 0}%`}
            subtitle="Clicks → Installs"
            icon={GetAppIcon}
            tooltip="Percentage of people who installed after clicking. Industry benchmark: 10-20%. Higher CVR = compelling app store page. Formula: (Installs ÷ Clicks) × 100"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Overall Efficiency"
            value={`${summary?.impressions > 0 ? ((summary.installs / summary.impressions) * 100).toFixed(3) : 0}%`}
            subtitle="Impressions → Installs"
            icon={AttachMoneyIcon}
            tooltip="End-to-end conversion rate from impression to install. Shows overall funnel efficiency. Target: >0.3%. Multiply CTR × CVR to get this number."
          />
        </Grid>
      </Grid>

      {/* Funnel Visualization */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ color: '#1a1a1a', fontWeight: 600 }}>
          Conversion Funnel
        </Typography>
        <Typography variant="body2" sx={{ mb: 3, color: '#666' }}>
          Visualize drop-off at each stage - identify where users are leaving
        </Typography>
        <ResponsiveContainer width="100%" height={350}>
          <BarChart data={funnelData} layout="vertical">
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              type="number" 
              tick={{ fill: '#666', fontSize: 12 }}
              stroke="#999"
            />
            <YAxis 
              type="category" 
              dataKey="stage" 
              tick={{ fill: '#666', fontSize: 12 }}
              stroke="#999"
              width={100}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
              labelStyle={{ color: '#333', fontWeight: 600 }}
              formatter={(value, name, props) => [
                `${value.toLocaleString()} (${props.payload.percentage}%)`,
                props.payload.stage
              ]}
            />
            <Bar dataKey="value" radius={[0, 8, 8, 0]}>
              {funnelData.map((entry, index) => (
                <Cell key={`cell-${index}`} fill={entry.color} />
              ))}
            </Bar>
          </BarChart>
        </ResponsiveContainer>
        <Box sx={{ mt: 2, p: 2, bgcolor: '#f5f5f5', borderRadius: 1 }}>
          <Typography variant="body2" sx={{ color: '#333' }}>
            <strong>Drop-off Analysis:</strong> {summary?.impressions > 0 && summary?.clicks > 0 && (
              <>
                {((1 - summary.clicks / summary.impressions) * 100).toFixed(1)}% drop from Impressions to Clicks, 
                {' '}{((1 - summary.installs / summary.clicks) * 100).toFixed(1)}% drop from Clicks to Installs
              </>
            )}
          </Typography>
        </Box>
      </Paper>

      {/* Cost Per Stage */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ color: '#1a1a1a', fontWeight: 600 }}>
          Cost Per Stage
        </Typography>
        <Typography variant="body2" sx={{ mb: 3, color: '#666' }}>
          Compare acquisition costs at each funnel stage
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={costData}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="stage" 
              tick={{ fill: '#666', fontSize: 12 }}
              stroke="#999"
            />
            <YAxis 
              tick={{ fill: '#666', fontSize: 12 }}
              stroke="#999"
              label={{ value: 'Cost ($)', angle: -90, position: 'insideLeft', fill: '#666' }}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
              labelStyle={{ color: '#333', fontWeight: 600 }}
              formatter={(value, name, props) => [`$${value.toFixed(2)}`, props.payload.label]}
            />
            <Bar dataKey="value" fill="#2e7d32" radius={[8, 8, 0, 0]} />
          </BarChart>
        </ResponsiveContainer>
      </Paper>

      {/* Conversion Rates Over Time */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom sx={{ color: '#1a1a1a', fontWeight: 600 }}>
          Conversion Rates Trend
        </Typography>
        <Typography variant="body2" sx={{ mb: 3, color: '#666' }}>
          Track CTR and CVR performance over time - spot trends and anomalies
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trends}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="date" 
              tick={{ fill: '#666', fontSize: 12 }}
              stroke="#999"
            />
            <YAxis 
              tick={{ fill: '#666', fontSize: 12 }}
              stroke="#999"
              label={{ value: 'Rate (%)', angle: -90, position: 'insideLeft', fill: '#666' }}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
              labelStyle={{ color: '#333', fontWeight: 600 }}
            />
            <Legend wrapperStyle={{ color: '#333' }} />
            <Line 
              type="monotone" 
              dataKey="ctr" 
              stroke="#1976d2" 
              strokeWidth={2}
              name="CTR (%)"
              dot={false}
            />
            <Line 
              type="monotone" 
              dataKey="cvr" 
              stroke="#2e7d32" 
              strokeWidth={2}
              name="CVR (%)"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </Paper>

      {/* Funnel Volume Trends */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ color: '#1a1a1a', fontWeight: 600 }}>
          Funnel Volume Over Time
        </Typography>
        <Typography variant="body2" sx={{ mb: 3, color: '#666' }}>
          Daily volume at each funnel stage - understand traffic patterns
        </Typography>
        <ResponsiveContainer width="100%" height={350}>
          <LineChart data={trends}>
            <CartesianGrid strokeDasharray="3 3" stroke="#e0e0e0" />
            <XAxis 
              dataKey="date" 
              tick={{ fill: '#666', fontSize: 12 }}
              stroke="#999"
            />
            <YAxis 
              yAxisId="left"
              tick={{ fill: '#666', fontSize: 12 }}
              stroke="#999"
              label={{ value: 'Impressions / Clicks', angle: -90, position: 'insideLeft', fill: '#666' }}
            />
            <YAxis 
              yAxisId="right"
              orientation="right"
              tick={{ fill: '#666', fontSize: 12 }}
              stroke="#999"
              label={{ value: 'Installs', angle: 90, position: 'insideRight', fill: '#666' }}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
              labelStyle={{ color: '#333', fontWeight: 600 }}
            />
            <Legend wrapperStyle={{ color: '#333' }} />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="impressions" 
              stroke="#1976d2" 
              strokeWidth={2}
              name="Impressions"
              dot={false}
            />
            <Line 
              yAxisId="left"
              type="monotone" 
              dataKey="clicks" 
              stroke="#42a5f5" 
              strokeWidth={2}
              name="Clicks"
              dot={false}
            />
            <Line 
              yAxisId="right"
              type="monotone" 
              dataKey="installs" 
              stroke="#2e7d32" 
              strokeWidth={2}
              name="Installs"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </Paper>
    </Container>
  );
}

export default FunnelDashboard;
