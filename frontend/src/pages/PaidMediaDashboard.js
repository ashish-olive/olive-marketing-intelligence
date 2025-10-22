import React, { useState, useEffect } from 'react';
import {
  Container, Grid, Typography, Paper, Table, TableBody, TableCell,
  TableContainer, TableHead, TableRow, Box, CircularProgress
} from '@mui/material';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';
import { getPaidChannels, getPaidCampaigns } from '../api/marketingApi';

function PaidMediaDashboard() {
  const [loading, setLoading] = useState(true);
  const [channels, setChannels] = useState([]);
  const [campaigns, setCampaigns] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const [channelsRes, campaignsRes] = await Promise.all([
        getPaidChannels(30),
        getPaidCampaigns(30)
      ]);
      setChannels(channelsRes.data);
      setCampaigns(campaignsRes.data);
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
        Paid Media Dashboard
      </Typography>
      <Typography variant="body1" gutterBottom sx={{ mb: 3, color: '#555555' }}>
        Channel and campaign performance analysis
      </Typography>

      {/* Channel Performance Chart */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Channel Performance Comparison
        </Typography>
        <ResponsiveContainer width="100%" height={300}>
          <BarChart data={channels}>
            <CartesianGrid strokeDasharray="3 3" />
            <XAxis dataKey="display_name" />
            <YAxis />
            <Tooltip />
            <Legend />
            <Bar dataKey="spend" fill="#8884d8" name="Spend ($)" />
            <Bar dataKey="installs" fill="#82ca9d" name="Installs" />
          </BarChart>
        </ResponsiveContainer>
      </Paper>

      {/* Channel Metrics Table */}
      <Paper sx={{ p: 3, mb: 4 }}>
        <Typography variant="h6" gutterBottom>
          Channel Metrics
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Channel</strong></TableCell>
                <TableCell align="right"><strong>Spend</strong></TableCell>
                <TableCell align="right"><strong>Installs</strong></TableCell>
                <TableCell align="right"><strong>CPI</strong></TableCell>
                <TableCell align="right"><strong>ROAS</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {channels.map((channel) => (
                <TableRow key={channel.channel}>
                  <TableCell>{channel.display_name}</TableCell>
                  <TableCell align="right">${channel.spend.toLocaleString()}</TableCell>
                  <TableCell align="right">{channel.installs.toLocaleString()}</TableCell>
                  <TableCell align="right">${channel.cpi.toFixed(2)}</TableCell>
                  <TableCell align="right">{channel.roas.toFixed(2)}x</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>

      {/* Campaign Performance Table */}
      <Paper sx={{ p: 3 }}>
        <Typography variant="h6" gutterBottom>
          Top Campaigns
        </Typography>
        <TableContainer>
          <Table>
            <TableHead>
              <TableRow>
                <TableCell><strong>Campaign</strong></TableCell>
                <TableCell><strong>Channel</strong></TableCell>
                <TableCell align="right"><strong>Spend</strong></TableCell>
                <TableCell align="right"><strong>Installs</strong></TableCell>
                <TableCell align="right"><strong>CPI</strong></TableCell>
                <TableCell align="right"><strong>ROAS</strong></TableCell>
              </TableRow>
            </TableHead>
            <TableBody>
              {campaigns.slice(0, 10).map((campaign, idx) => (
                <TableRow key={idx}>
                  <TableCell>{campaign.campaign}</TableCell>
                  <TableCell>{campaign.channel}</TableCell>
                  <TableCell align="right">${campaign.spend.toLocaleString()}</TableCell>
                  <TableCell align="right">{campaign.installs.toLocaleString()}</TableCell>
                  <TableCell align="right">${campaign.cpi.toFixed(2)}</TableCell>
                  <TableCell align="right">{campaign.roas.toFixed(2)}x</TableCell>
                </TableRow>
              ))}
            </TableBody>
          </Table>
        </TableContainer>
      </Paper>
    </Container>
  );
}

export default PaidMediaDashboard;
