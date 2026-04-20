import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { CssBaseline, ThemeProvider, createTheme } from '@mui/material';
import Layout from './components/Layout';
import BrowsePage from './pages/BrowsePage';
import UploadPage from './pages/UploadPage';
import DownloadPage from './pages/DownloadPage';
import SettingsPage from './pages/SettingsPage';

const theme = createTheme({
  palette: { mode: 'light' },
});

export default function App() {
  return (
    <ThemeProvider theme={theme}>
      <CssBaseline />
      <BrowserRouter>
        <Routes>
          <Route element={<Layout />}>
            <Route path="/" element={<BrowsePage />} />
            <Route path="/upload" element={<UploadPage />} />
            <Route path="/download" element={<DownloadPage />} />
            <Route path="/settings" element={<SettingsPage />} />
          </Route>
        </Routes>
      </BrowserRouter>
    </ThemeProvider>
  );
}
