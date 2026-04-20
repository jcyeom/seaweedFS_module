import { useEffect, useState } from 'react';
import {
  Box, Button, TextField, Typography, Paper, Stack, Checkbox,
  FormControl, InputLabel, Select, MenuItem, FormControlLabel,
} from '@mui/material';
import CloudDownloadIcon from '@mui/icons-material/CloudDownload';
import ProgressPanel from '../components/ProgressPanel';
import { startDownload, getStats } from '../api/client';
import type { CategoryStat } from '../types';

export default function DownloadPage() {
  const [remoteDir, setRemoteDir] = useState('accept');
  const [localDir, setLocalDir] = useState('');
  const [category, setCategory] = useState('');
  const [skipExisting, setSkipExisting] = useState(true);
  const [taskId, setTaskId] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);
  const [categories, setCategories] = useState<CategoryStat[]>([]);

  useEffect(() => {
    getStats(remoteDir).then((d) => setCategories(d.categories)).catch(() => {});
  }, [remoteDir]);

  const handleStart = async () => {
    if (!localDir.trim()) return;
    setStarting(true);
    try {
      const { task_id } = await startDownload(remoteDir, localDir, category || undefined, skipExisting);
      setTaskId(task_id);
    } catch { /* ignore */ }
    setStarting(false);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Download from SeaweedFS</Typography>
      <Paper sx={{ p: 3, maxWidth: 600 }}>
        <Stack spacing={2}>
          <FormControl fullWidth>
            <InputLabel>Remote Directory</InputLabel>
            <Select value={remoteDir} label="Remote Directory" onChange={(e) => { setRemoteDir(e.target.value); setCategory(''); }}>
              <MenuItem value="accept">accept</MenuItem>
              <MenuItem value="non_accept">non_accept</MenuItem>
            </Select>
          </FormControl>
          <FormControl fullWidth>
            <InputLabel>Category (optional)</InputLabel>
            <Select value={category} label="Category (optional)" onChange={(e) => setCategory(e.target.value)}>
              <MenuItem value="">All</MenuItem>
              {categories.map((c) => (
                <MenuItem key={c.category} value={c.category}>
                  {c.category} ({c.count.toLocaleString()})
                </MenuItem>
              ))}
            </Select>
          </FormControl>
          <TextField
            label="Local Download Path"
            value={localDir}
            onChange={(e) => setLocalDir(e.target.value)}
            placeholder="/home/jcyeom/work/safety/download"
            fullWidth
          />
          <FormControlLabel
            control={<Checkbox checked={skipExisting} onChange={(e) => setSkipExisting(e.target.checked)} />}
            label="Skip existing files"
          />
          <Button
            variant="contained"
            startIcon={<CloudDownloadIcon />}
            onClick={handleStart}
            disabled={starting || !localDir.trim()}
            size="large"
          >
            {starting ? 'Starting...' : 'Start Download'}
          </Button>
        </Stack>
      </Paper>

      <ProgressPanel taskType="download" taskId={taskId} />
    </Box>
  );
}
