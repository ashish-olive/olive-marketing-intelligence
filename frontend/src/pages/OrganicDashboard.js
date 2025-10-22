import React, { useState, useEffect } from 'react';
import { Container, Grid, Typography, Paper, Box, CircularProgress } from '@mui/material';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import KPICard from '../components/KPICard';
import { getOrganicSummary, getOrganicTrends } from '../api/marketingApi';
import StarIcon from '@mui/icons-material/Star';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import ThumbUpIcon from '@mui/icons-material/ThumbUp';

function OrganicDashboard() {
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
        getOrganicSummary(30),
        getOrganicTrends(30)
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
        App Store & Brand Performance
      </Typography>
      <Typography variant="body1" gutterBottom sx={{ mb: 3, color: '#555555' }}>
        Non-paid growth, app store visibility, and brand sentiment metrics
      </Typography>

      {/* KPI Cards */}
      <Grid container spacing={3} sx={{ mb: 4 }}>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Organic Installs"
            value={(summary?.organic_installs || 0).toLocaleString()}
            subtitle="Last 30 days"
            icon={TrendingUpIcon}
            tooltip="Users who installed your app without clicking on paid ads - from app store search, word-of-mouth, press coverage, or social media. These are 'free' users with typically higher LTV."
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="App Store Rank"
            value={`#${Math.round(summary?.avg_app_store_rank || 0)}`}
            subtitle="Average rank"
            icon={StarIcon}
            tooltip="Your app's average ranking position in the app store category over the last 30 days. Lower number = better visibility. Top 10 = featured placement. Rank affects organic install volume."
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Sentiment Score"
            value={(summary?.avg_sentiment_score || 0).toFixed(2)}
            subtitle="Social sentiment"
            icon={ThumbUpIcon}
            tooltip="Average sentiment of social media mentions and reviews (0-1 scale). Above 0.7 = positive brand perception. Below 0.5 = negative sentiment requiring attention. Affects organic growth."
          />
        </Grid>
        <Grid item xs={12} sm={6} md={3}>
          <KPICard
            title="Social Mentions"
            value={(summary?.total_social_mentions || 0).toLocaleString()}
            subtitle="Total mentions"
            icon={TrendingUpIcon}
            tooltip="Total times your app was mentioned on social media, forums, and review sites in the last 30 days. Higher mentions = more brand awareness and potential for viral growth."
          />
        </Grid>
      </Grid>

      {/* Organic Trends Chart */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Organic Install Trends
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Line
              type="monotone"
              dataKey="organic_installs"
              stroke="#82ca9d"
              name="Organic Installs"
            />
          </LineChart>
        </ResponsiveContainer>
      </Paper>

      {/* App Store Rank Trend */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          App Store Rank & Sentiment
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <LineChart data={trends}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="date" />
            <YAxis yAxisId="left" reversed />
            <YAxis yAxisId="right" orientation="right" domain={[0, 1]} />
            <Tooltip />
            <Legend />
            <Line
              yAxisId="left"
              type="monotone"
              dataKey="app_store_rank"
              stroke="#8884d8"
              name="App Store Rank"
            />
            <Line
              yAxisId="right"
              type="monotone"
              dataKey="sentiment_score"
              stroke="#ffc658"
              name="Sentiment Score"
            />
          </LineChart>
        </ResponsiveContainer>
      </Paper>
    </Container>
  );
}

export default OrganicDashboard;
