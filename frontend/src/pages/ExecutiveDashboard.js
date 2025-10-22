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
      <Typography variant="h4" gutterBottom>
        Executive Dashboard
      </Typography>
      <Typography variant="body1" color="text.secondary" gutterBottom sx={{ mb: 3 }}>
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
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Total Installs"
            value={(summary?.total_installs || 0).toLocaleString()}
            subtitle={`${(summary?.organic_installs || 0).toLocaleString()} organic`}
            icon={PeopleIcon}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Blended CAC"
            value={`$${summary?.blended_cac?.toFixed(2) || 0}`}
            subtitle="Cost per install"
            icon={TrendingUpIcon}
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="ROAS (30d)"
            value={`${summary?.roas_30d?.toFixed(2) || 0}x`}
            subtitle={`LTV/CAC: ${summary?.ltv_cac_ratio?.toFixed(2) || 0}x`}
            icon={TrendingUpIcon}
          />
        </Grid>
      </Grid>

      {/* Trends Chart */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Daily Performance Trends
        </Typography>
        <ResponsiveContainer width="100%" height={400}>
          <LineChart data={trends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis yAxisId="left" />
            <YAxis yAxisId="right" orientation="right" />
            <Tooltip />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="spend"
              stroke="#8884d8"
              name="Spend ($)"
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="installs"
              stroke="#82ca9d"
              name="Installs"
            />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="cpi"
              stroke="#ffc658"
              name="CPI ($)"
            />
          </LineChart>
        </ResponsiveContainer>
      </Paper>
    </Container>
  );
}

export default ExecutiveDashboard;
