import { useState } from 'react';
import {
  Box, Button, TextField, Typography, Paper, Stack,
  FormControl, InputLabel, Select, MenuItem,
} from '@mui/material';
import CloudUploadIcon from '@mui/icons-material/CloudUpload';
import ProgressPanel from '../components/ProgressPanel';
import { startUpload } from '../api/client';

export default function UploadPage() {
  const [localDir, setLocalDir] = useState('');
  const [remoteDir, setRemoteDir] = useState('accept');
  const [pattern, setPattern] = useState('*.jpg');
  const [taskId, setTaskId] = useState<string | null>(null);
  const [starting, setStarting] = useState(false);

  const handleStart = async () => {
    if (!localDir.trim()) return;
    setStarting(true);
    try {
      const { task_id } = await startUpload(localDir, remoteDir, pattern);
      setTaskId(task_id);
    } catch { /* ignore */ }
    setStarting(false);
  };

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Upload to SeaweedFS</Typography>
      <Paper sx={{ p: 3, maxWidth: 600 }}>
        <Stack spacing={2}>
          <TextField
            label="Local Folder Path"
            value={localDir}
            onChange={(e) => setLocalDir(e.target.value)}
            placeholder="/home/jcyeom/work/safety/260410_organized/accept"
            fullWidth
          />
          <FormControl fullWidth>
            <InputLabel>Remote Directory</InputLabel>
            <Select value={remoteDir} label="Remote Directory" onChange={(e) => setRemoteDir(e.target.value)}>
              <MenuItem value="accept">accept</MenuItem>
              <MenuItem value="non_accept">non_accept</MenuItem>
            </Select>
          </FormControl>
          <TextField label="File Pattern" value={pattern} onChange={(e) => setPattern(e.target.value)} />
          <Button
            variant="contained"
            startIcon={<CloudUploadIcon />}
            onClick={handleStart}
            disabled={starting || !localDir.trim()}
            size="large"
          >
            {starting ? 'Starting...' : 'Start Upload'}
          </Button>
        </Stack>
      </Paper>

      <ProgressPanel taskType="upload" taskId={taskId} />
    </Box>
  );
}
