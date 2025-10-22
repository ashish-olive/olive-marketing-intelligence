import React from 'react';
import Card from '@mui/material/Card';
import CardContent from '@mui/material/CardContent';
import Typography from '@mui/material/Typography';
import Box from '@mui/material/Box';
import Tooltip from '@mui/material/Tooltip';
import IconButton from '@mui/material/IconButton';
import InfoOutlinedIcon from '@mui/icons-material/InfoOutlined';
import TrendingUpIcon from '@mui/icons-material/TrendingUp';
import TrendingDownIcon from '@mui/icons-material/TrendingDown';

function KPICard({ title, value, subtitle, trend, trendValue, icon: Icon, tooltip }) {
  const trendColor = trend === 'up' ? 'success.main' : trend === 'down' ? 'error.main' : 'text.secondary';
  const TrendIcon = trend === 'up' ? TrendingUpIcon : trend === 'down' ? TrendingDownIcon : null;

  return (
    <Card sx={{ height: '100%' }}>
      <CardContent>
        <Box sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', mb: 2 }}>
          <Box sx={{ display: 'flex', alignItems: 'center', flex: 1 }}>
            <Typography variant="body2" gutterBottom sx={{ color: '#333333', fontWeight: 500 }}>
              {title}
            </Typography>
            {tooltip && (
              <Tooltip title={tooltip} arrow placement="top">
                <IconButton size="small" sx={{ ml: 0.5, p: 0.5 }}>
                  <InfoOutlinedIcon sx={{ fontSize: 16, color: '#666' }} />
                </IconButton>
              </Tooltip>
            )}
          </Box>
          {Icon && <Icon color="primary" />}
        </Box>
        <Typography variant="h4" component="div" sx={{ mb: 1, color: '#1a1a1a', fontWeight: 600 }}>
          {value}
        </Typography>
        {subtitle && (
          <Typography variant="body2" sx={{ color: '#555555' }}>
            {subtitle}
          </Typography>
        )}
        {trendValue && TrendIcon && (
          <Box sx={{ display: 'flex', alignItems: 'center', mt: 1 }}>
            <TrendIcon sx={{ fontSize: 16, color: trendColor, mr: 0.5 }} />
            <Typography variant="body2" sx={{ color: trendColor }}>
              {trendValue}
            </Typography>
          </Box>
        )}
      </CardContent>
    </Card>
  );
}

export default KPICard;
