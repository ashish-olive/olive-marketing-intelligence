import React from 'react';
import { BrowserRouter as Router, Routes, Route, Navigate } from 'react-router-dom';
import Box from '@mui/material/Box';

import Navbar from './components/Navbar';
import ExecutiveDashboard from './pages/ExecutiveDashboard';
import PaidMediaDashboard from './pages/PaidMediaDashboard';
import FunnelDashboard from './pages/FunnelDashboard';
import OrganicDashboard from './pages/OrganicDashboard';
import SignalsDashboard from './pages/SignalsDashboard';
import ModelingDashboard from './pages/ModelingDashboard';

function App() {
  return (
    <Router>
      <Box sx={{ display: 'flex', flexDirection: 'column', minHeight: '100vh' }}>
        <Navbar />
        <Box component="main" sx={{ flexGrow: 1, p: 3, mt: 8 }}>
          <Routes>
            <Route path="/" element={<Navigate to="/executive" replace />} />
            <Route path="/executive" element={<ExecutiveDashboard />} />
            <Route path="/paid-media" element={<PaidMediaDashboard />} />
            <Route path="/funnel" element={<FunnelDashboard />} />
            <Route path="/organic" element={<OrganicDashboard />} />
            <Route path="/signals" element={<SignalsDashboard />} />
            <Route path="/modeling" element={<ModelingDashboard />} />
          </Routes>
        </Box>
      </Box>
    </Router>
  );
}

export default App;
