import React, { useState, useEffect } from 'react';
import {
  Container, Typography, Paper, Box, CircularProgress, Chip, Card,
  CardContent, Button, Grid
} from '@mui/material';
import WarningIcon from '@mui/icons-material/Warning';
import InfoIcon from '@mui/icons-material/Info';
import ErrorIcon from '@mui/icons-material/Error';
import { getSignals, dismissSignal } from '../api/marketingApi';

function SignalsDashboard() {
  const [loading, setLoading] = useState(true);
  const [signals, setSignals] = useState([]);
  const [error, setError] = useState(null);

  useEffect(() => {
    loadData();
  }, []);

  const loadData = async () => {
    try {
      setLoading(true);
      const response = await getSignals(30, 'all');
      setSignals(response.data);
      setError(null);
    } catch (err) {
      console.error('Error loading signals:', err);
      setError('Failed to load signals. Please ensure the backend is running.');
    } finally {
      setLoading(false);
    }
  };

  const handleDismiss = async (signalId) => {
    try {
      await dismissSignal(signalId);
      setSignals(signals.filter(s => s.id !== signalId));
    } catch (err) {
      console.error('Error dismissing signal:', err);
    }
  };

  const getSeverityIcon = (severity) => {
    switch (severity) {
      case 'critical':
        return <ErrorIcon color="error" />;
      case 'warning':
        return <WarningIcon color="warning" />;
      default:
        return <InfoIcon color="info" />;
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'critical':
        return 'error';
      case 'warning':
        return 'warning';
      default:
        return 'info';
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
        Performance Signals
      </Typography>
      <Typography variant="body1" gutterBottom sx={{ mb: 3, color: '#555555' }}>
        AI-powered insights and recommended actions
      </Typography>

      {signals.length === 0 ? (
        <Paper sx={{ p: 4, textAlign: 'center' }}>
          <InfoIcon sx={{ fontSize: 48, color: 'text.secondary', mb: 2 }} />
          <Typography variant="h6" color="text.secondary">
            No active signals
          </Typography>
          <Typography variant="body2" color="text.secondary">
            All systems performing normally
          </Typography>
        </Paper>
      ) : (
        <Grid container spacing={3}>
          {signals.map((signal) => (
            <Grid item xs={12} key={signal.id}>
              <Card>
                <CardContent>
                  <Box sx={{ display: 'flex', alignItems: 'flex-start', mb: 2 }}>
                    <Box sx={{ mr: 2 }}>
                      {getSeverityIcon(signal.severity)}
                    </Box>
                    <Box sx={{ flexGrow: 1 }}>
                      <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                        <Typography variant="h6" sx={{ flexGrow: 1 }}>
                          {signal.title}
                        </Typography>
                        <Chip
                          label={signal.severity.toUpperCase()}
                          color={getSeverityColor(signal.severity)}
                          size="small"
                          sx={{ mr: 1 }}
                        />
                        <Chip
                          label={`Priority: ${signal.priority_score.toFixed(0)}`}
                          size="small"
                          variant="outlined"
                        />
                      </Box>
                      <Typography variant="body2" color="text.secondary" sx={{ mb: 2 }}>
                        {signal.description}
                      </Typography>
                      <Paper sx={{ p: 2, bgcolor: 'primary.light', mb: 2 }}>
                        <Typography variant="subtitle2" gutterBottom>
                          <strong>Recommended Action:</strong>
                        </Typography>
                        <Typography variant="body2">
                          {signal.recommended_action}
                        </Typography>
                        {signal.predicted_impact && Object.keys(signal.predicted_impact).length > 0 && (
                          <Box sx={{ mt: 1 }}>
                            <Typography variant="caption" color="text.secondary">
                              Predicted Impact: {JSON.stringify(signal.predicted_impact)}
                            </Typography>
                          </Box>
                        )}
                      </Paper>
                      <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                        <Typography variant="caption" color="text.secondary">
                          Detected: {signal.date} | Confidence: {(signal.confidence * 100).toFixed(0)}%
                        </Typography>
                        <Button
                          size="small"
                          onClick={() => handleDismiss(signal.id)}
                        >
                          Dismiss
                        </Button>
                      </Box>
                    </Box>
                  </Box>
                </CardContent>
              </Card>
            </Grid>
          ))}
        </Grid>
      )}
    </Container>
  );
}

export default SignalsDashboard;
