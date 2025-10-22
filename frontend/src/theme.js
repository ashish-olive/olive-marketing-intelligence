import { createTheme } from '@mui/material/styles';

// High-contrast, professional theme for Marketing Intelligence
const theme = createTheme({
  palette: {
    primary: {
      main: '#1976d2',
      dark: '#115293',
      light: '#42a5f5',
    },
    secondary: {
      main: '#dc004e',
    },
    success: {
      main: '#2e7d32',
    },
    error: {
      main: '#d32f2f',
    },
    warning: {
      main: '#ed6c02',
    },
    background: {
      default: '#fafafa',      // Slightly darker background
      paper: '#ffffff',
    },
    text: {
      primary: '#1a1a1a',      // Very dark for maximum contrast
      secondary: '#333333',    // Dark gray for secondary text
    },
  },
  typography: {
    fontFamily: '"Inter", "Roboto", "Helvetica", "Arial", sans-serif',
    h1: {
      fontSize: '2.5rem',
      fontWeight: 600,
      color: '#1a1a1a',
    },
    h2: {
      fontSize: '2rem',
      fontWeight: 600,
      color: '#1a1a1a',
    },
    h3: {
      fontSize: '1.75rem',
      fontWeight: 600,
      color: '#1a1a1a',
    },
    h4: {
      fontSize: '1.5rem',
      fontWeight: 600,
      color: '#1a1a1a',
    },
    h5: {
      fontSize: '1.25rem',
      fontWeight: 600,
      color: '#1a1a1a',
    },
    h6: {
      fontSize: '1rem',
      fontWeight: 600,
      color: '#1a1a1a',
    },
    body1: {
      fontSize: '1rem',
      color: '#1a1a1a',
      lineHeight: 1.6,
    },
    body2: {
      fontSize: '0.875rem',
      color: '#333333',
      lineHeight: 1.5,
    },
    caption: {
      fontSize: '0.75rem',
      color: '#555555',
      lineHeight: 1.4,
    },
  },
  components: {
    MuiCard: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
          borderRadius: 8,
        },
      },
    },
    MuiPaper: {
      styleOverrides: {
        root: {
          boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        },
      },
    },
    MuiTypography: {
      styleOverrides: {
        colorTextSecondary: {
          color: '#333333', // Much darker secondary text for better contrast
        },
      },
    },
    MuiTableCell: {
      styleOverrides: {
        root: {
          color: '#1a1a1a', // Dark text in tables
        },
      },
    },
  },
});

export default theme;
