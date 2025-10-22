import React, { useState, useEffect } from 'react';
import { Container, Grid, Typography, Paper, Box, CircularProgress } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import PeopleIcon from '@mui/icons-material/People';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import KPICard from '../components/KPICard';
import { getExecutiveSummary, getExecutiveTrends } from '../api/marketingApi';

function ExecutiveDashboard() {
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
        getExecutiveSummary(30),
        getExecutiveTrends(30)
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

  return (
    <Container maxWidth="xl">
      <Typography variant="h4" gutterBottom sx={{ color: '#1a1a1a', fontWeight: 600 }}>
        Executive Dashboard
      </Typography>
      <Typography variant="body1" gutterBottom sx={{ mb: 3, color: '#555555' }}>
        High-level performance metrics and trends
      </Typography>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Total Spend"
            value={`$${summary?.total_spend?.toLocaleString() || 0}`}
            subtitle="Last 30 days"
            icon={AttachMoneyIcon}
            tooltip="Total marketing spend across all paid channels (Meta, Google, TikTok, Apple Search) in the last 30 days. This is your total acquisition budget."
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Total Installs"
            value={(summary?.total_installs || 0).toLocaleString()}
            subtitle={`${summary?.organic_installs?.toLocaleString() || 0} organic`}
            icon={PeopleIcon}
            tooltip="Total new users acquired in the last 30 days, including both paid (from marketing campaigns) and organic (from app store search, word-of-mouth, etc.) installs."
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Blended CAC"
            value={`$${summary?.blended_cac?.toFixed(2) || 0}`}
            subtitle="Cost per install"
            icon={TrendingUpIcon}
            tooltip="Blended Customer Acquisition Cost - average cost to acquire one user across all channels. Calculated as Total Spend ÷ Total Installs. Lower is better. Target: <$3.00"
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="ROAS (30d)"
            value={`${summary?.roas_30d?.toFixed(2) || 0}x`}
            subtitle={`LTV/CAC: ${summary?.ltv_cac_ratio?.toFixed(2) || 0}x`}
            icon={TrendingUpIcon}
            tooltip="Return on Ad Spend - revenue generated divided by marketing spend over 30 days. Above 1.0x means profitable. LTV/CAC ratio shows long-term profitability. Target ROAS: 3-5x"
          />
        </Grid>
      </Grid>

      {/* Trends Chart */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ color: '#1a1a1a', fontWeight: 600 }}>
          Daily Performance Trends
        </Typography>
        <Typography variant="body2" sx={{ mb: 2, color: '#666' }}>
          Spend and Installs over time (CPI excluded due to scale difference)
        </Typography>
        <ResponsiveContainer width="100%" height={400}>
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
              label={{ value: 'Spend ($)', angle: -90, position: 'insideLeft', fill: '#666' }}
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
              dataKey="spend"
              stroke="#1976d2"
              strokeWidth={2}
              name="Spend ($)"
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

      {/* CPI Trends Chart - Separate due to scale */}
      <Paper sx={{ p: 3, mt: 3 }}>
        <Typography variant="h6" gutterBottom sx={{ color: '#1a1a1a', fontWeight: 600 }}>
          Cost Per Install (CPI) Trends
        </Typography>
        <Typography variant="body2" sx={{ mb: 2, color: '#666' }}>
          Average CPI across all channels over time
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
              label={{ value: 'CPI ($)', angle: -90, position: 'insideLeft', fill: '#666' }}
              domain={[0, 'auto']}
            />
            <Tooltip 
              contentStyle={{ backgroundColor: '#fff', border: '1px solid #ccc' }}
              labelStyle={{ color: '#333', fontWeight: 600 }}
              formatter={(value) => `$${value.toFixed(2)}`}
            />
            <Legend wrapperStyle={{ color: '#333' }} />
            <Line
              type="monotone"
              dataKey="cpi"
              stroke="#f57c00"
              strokeWidth={3}
              name="CPI ($)"
              dot={false}
            />
          </LineChart>
        </ResponsiveContainer>
      </Paper>
    </Container>
  );
}

export default ExecutiveDashboard;
