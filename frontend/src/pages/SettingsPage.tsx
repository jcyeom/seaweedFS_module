import { useEffect, useState } from 'react';
import {
  Box, Button, TextField, Typography, Alert, Stack, Paper, CircularProgress,
} from '@mui/material';
import type { AppConfig } from '../types';
import { getSettings, updateSettings, testConnection } from '../api/client';

export default function SettingsPage() {
  const [cfg, setCfg] = useState<AppConfig | null>(null);
  const [saving, setSaving] = useState(false);
  const [testing, setTesting] = useState(false);
  const [msg, setMsg] = useState<{ type: 'success' | 'error'; text: string } | null>(null);

  useEffect(() => { getSettings().then(setCfg); }, []);

  if (!cfg) return <CircularProgress />;

  const handleSave = async () => {
    setSaving(true);
    setMsg(null);
    try {
      const updated = await updateSettings(cfg);
      setCfg(updated);
      setMsg({ type: 'success', text: 'Settings saved.' });
    } catch {
      setMsg({ type: 'error', text: 'Failed to save settings.' });
    }
    setSaving(false);
  };

  const handleTest = async () => {
    setTesting(true);
    setMsg(null);
    try {
      const result = await testConnection();
      if (result.ok) {
        setMsg({ type: 'success', text: `Connected. SeaweedFS ${result.version}` });
      } else {
        setMsg({ type: 'error', text: `Connection failed: ${result.error}` });
      }
    } catch {
      setMsg({ type: 'error', text: 'Connection test failed.' });
    }
    setTesting(false);
  };

  const update = (field: keyof AppConfig, value: string) => {
    const numFields: (keyof AppConfig)[] = ['max_workers', 'retry_count', 'page_size', 'list_page_size', 'timeout'];
    setCfg({ ...cfg, [field]: numFields.includes(field) ? Number(value) || 0 : value });
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Settings</Typography>
      <Paper sx={{ p: 3, maxWidth: 600 }}>
        <Stack spacing={2}>
          <TextField label="SeaweedFS Filer URL" value={cfg.filer_url} onChange={(e) => update('filer_url', e.target.value)} fullWidth />
          <TextField label="Max Workers" type="number" value={cfg.max_workers} onChange={(e) => update('max_workers', e.target.value)} />
          <TextField label="Retry Count" type="number" value={cfg.retry_count} onChange={(e) => update('retry_count', e.target.value)} />
          <TextField label="Page Size (UI)" type="number" value={cfg.page_size} onChange={(e) => update('page_size', e.target.value)} />
          <TextField label="List Page Size (API)" type="number" value={cfg.list_page_size} onChange={(e) => update('list_page_size', e.target.value)} />
          <TextField label="Timeout (seconds)" type="number" value={cfg.timeout} onChange={(e) => update('timeout', e.target.value)} />

          <Stack direction="row" spacing={2}>
            <Button variant="contained" onClick={handleSave} disabled={saving}>
              {saving ? 'Saving...' : 'Save'}
            </Button>
            <Button variant="outlined" onClick={handleTest} disabled={testing}>
              {testing ? 'Testing...' : 'Test Connection'}
            </Button>
          </Stack>

          {msg && <Alert severity={msg.type}>{msg.text}</Alert>}
        </Stack>
      </Paper>
    </Box>
  );
}
