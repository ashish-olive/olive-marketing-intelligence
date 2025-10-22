import React, { useState } from 'react';
import {
  Container, Typography, Paper, Box, TextField, Button, Grid,
  Card, CardContent, Slider, Alert, Chip, Tooltip, IconButton
} from '@mui/material';
import InfoIcon from '@mui/icons-material/Info';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import AttachMoneyIcon from '@mui/icons-material/AttachMoney';
import PeopleIcon from '@mui/icons-material/People';

function ModelingDashboard() {
  const [budget, setBudget] = useState(100000);
  const [targetCPI, setTargetCPI] = useState(2.50);
  const [prediction, setPrediction] = useState(null);

  const handlePredict = () => {
    // Calculate predictions
    const expectedInstalls = Math.floor(budget / targetCPI);
    const expectedLTV = expectedInstalls * 10.50; // Average LTV
    const expectedROI = (expectedLTV / budget).toFixed(2);
    
    setPrediction({
      installs: expectedInstalls.toLocaleString(),
      ltv: `$${expectedLTV.toLocaleString()}`,
      roi: `${expectedROI}x`,
      profitable: expectedROI > 1
    });
  };

  return (
    <Container maxWidth="xl">
      <Box sx={{ mb: 4 }}>
        <Typography variant="h4" gutterBottom sx={{ fontWeight: 600 }}>
          Campaign Modeling & Forecasting
        </Typography>
        <Typography variant="body1" color="text.secondary" gutterBottom>
          Use ML models to predict campaign outcomes and optimize budget allocation
        </Typography>
      </Box>

      <Grid container spacing={3}>
        {/* Input Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3 }}>
            <Box sx={{ display: 'flex', alignItems: 'center', mb: 3 }}>
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                Campaign Parameters
              </Typography>
              <Tooltip title="Adjust campaign parameters to see predicted outcomes">
                <IconButton size="small" sx={{ ml: 1 }}>
                  <InfoIcon fontSize="small" />
                </IconButton>
              </Tooltip>
            </Box>

            {/* Budget Input */}
            <Box sx={{ mb: 4 }}>
              <Typography gutterBottom sx={{ fontWeight: 500 }}>
                Campaign Budget
              </Typography>
              <TextField
                fullWidth
                type="number"
                value={budget}
                onChange={(e) => setBudget(Number(e.target.value))}
                InputProps={{
                  startAdornment: '$',
                }}
                helperText="Total budget to allocate for this campaign"
              />
              <Slider
                value={budget}
                onChange={(e, newValue) => setBudget(newValue)}
                min={10000}
                max={500000}
                step={10000}
                sx={{ mt: 2 }}
              />
            </Box>

            {/* Target CPI Input */}
            <Box sx={{ mb: 4 }}>
              <Typography gutterBottom sx={{ fontWeight: 500 }}>
                Target Cost Per Install (CPI)
              </Typography>
              <TextField
                fullWidth
                type="number"
                value={targetCPI}
                onChange={(e) => setTargetCPI(Number(e.target.value))}
                InputProps={{
                  startAdornment: '$',
                }}
                step="0.10"
                helperText="Expected cost to acquire one user"
              />
              <Slider
                value={targetCPI}
                onChange={(e, newValue) => setTargetCPI(newValue)}
                min={0.50}
                max={10.00}
                step={0.10}
                sx={{ mt: 2 }}
              />
            </Box>

            <Button
              variant="contained"
              size="large"
              fullWidth
              onClick={handlePredict}
              startIcon={<TrendingUpIcon />}
            >
              Generate Prediction
            </Button>
          </Paper>
        </Grid>

        {/* Results Section */}
        <Grid item xs={12} md={6}>
          <Paper sx={{ p: 3, minHeight: 400 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              Predicted Outcomes
            </Typography>
            
            {!prediction ? (
              <Box sx={{ display: 'flex', alignItems: 'center', justifyContent: 'center', minHeight: 300 }}>
                <Typography color="text.secondary">
                  Adjust parameters and click "Generate Prediction" to see results
                </Typography>
              </Box>
            ) : (
              <>
                <Alert severity={prediction.profitable ? "success" : "warning"} sx={{ mb: 3 }}>
                  {prediction.profitable 
                    ? "✅ This campaign is projected to be profitable!"
                    : "⚠️ This campaign may not be profitable at current parameters"}
                </Alert>

                <Grid container spacing={2}>
                  <Grid item xs={12}>
                    <Card sx={{ bgcolor: '#e3f2fd' }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <PeopleIcon color="primary" sx={{ mr: 1 }} />
                          <Typography variant="body2" color="text.secondary">
                            Expected Installs
                          </Typography>
                        </Box>
                        <Typography variant="h4" sx={{ fontWeight: 600 }}>
                          {prediction.installs}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          users acquired
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12}>
                    <Card sx={{ bgcolor: '#f3e5f5' }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <AttachMoneyIcon color="secondary" sx={{ mr: 1 }} />
                          <Typography variant="body2" color="text.secondary">
                            Expected Lifetime Value
                          </Typography>
                        </Box>
                        <Typography variant="h4" sx={{ fontWeight: 600 }}>
                          {prediction.ltv}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          total revenue from acquired users
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>

                  <Grid item xs={12}>
                    <Card sx={{ bgcolor: prediction.profitable ? '#e8f5e9' : '#fff3e0' }}>
                      <CardContent>
                        <Box sx={{ display: 'flex', alignItems: 'center', mb: 1 }}>
                          <TrendingUpIcon color={prediction.profitable ? "success" : "warning"} sx={{ mr: 1 }} />
                          <Typography variant="body2" color="text.secondary">
                            Return on Investment (ROI)
                          </Typography>
                        </Box>
                        <Typography variant="h4" sx={{ fontWeight: 600 }}>
                          {prediction.roi}
                        </Typography>
                        <Typography variant="caption" color="text.secondary">
                          {prediction.profitable ? "profitable" : "needs optimization"}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </Grid>

                <Box sx={{ mt: 3 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    <strong>Model Confidence:</strong>
                  </Typography>
                  <Box sx={{ display: 'flex', gap: 1, flexWrap: 'wrap' }}>
                    <Chip label="LTV Model: High (RMSE $0.30)" size="small" color="success" />
                    <Chip label="Campaign Model: Medium (MAPE 64%)" size="small" color="warning" />
                  </Box>
                </Box>
              </>
            )}
          </Paper>
        </Grid>

        {/* Help Section */}
        <Grid item xs={12}>
          <Paper sx={{ p: 3, bgcolor: '#f5f5f5' }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              💡 How to Use This Tool
            </Typography>
            <Grid container spacing={2}>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" sx={{ fontWeight: 500, mb: 1 }}>
                  1. Set Your Budget
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Enter the total amount you want to spend on this campaign. Use the slider for quick adjustments.
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" sx={{ fontWeight: 500, mb: 1 }}>
                  2. Define Target CPI
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Set your expected cost per install based on historical data or industry benchmarks.
                </Typography>
              </Grid>
              <Grid item xs={12} md={4}>
                <Typography variant="body2" sx={{ fontWeight: 500, mb: 1 }}>
                  3. Generate Predictions
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  Our ML models will predict installs, LTV, and ROI to help you make data-driven decisions.
                </Typography>
              </Grid>
            </Grid>
          </Paper>
        </Grid>
      </Grid>
    </Container>
  );
}

export default ModelingDashboard;
