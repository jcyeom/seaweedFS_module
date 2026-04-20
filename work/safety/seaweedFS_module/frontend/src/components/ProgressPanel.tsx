import { useEffect, useRef, useState } from 'react';
import { LinearProgress, Typography, Paper, Alert, Button, Chip, Stack } from '@mui/material';
import type { TaskState } from '../types';
import { cancelTask } from '../api/client';

interface Props {
  taskType: 'upload' | 'download';
  taskId: string | null;
}

export default function ProgressPanel({ taskType, taskId }: Props) {
  const [state, setState] = useState<TaskState | null>(null);
  const esRef = useRef<EventSource | null>(null);

  useEffect(() => {
    if (!taskId) return;
    setState(null);
    const es = new EventSource(`/api/${taskType}/${taskId}/progress`);
    esRef.current = es;
    es.onmessage = (e) => {
      const data: TaskState = JSON.parse(e.data);
      setState(data);
      if (['completed', 'cancelled', 'failed'].includes(data.status)) {
        es.close();
      }
    };
    es.onerror = () => es.close();
    return () => es.close();
  }, [taskId, taskType]);

  if (!taskId || !state) return null;

  const pct = state.total > 0 ? ((state.completed + state.failed + state.skipped) / state.total) * 100 : 0;
  const done = ['completed', 'cancelled', 'failed'].includes(state.status);

  const handleCancel = () => {
    cancelTask(taskType, taskId);
  };

  return (
    <Paper sx={{ p: 2, mt: 2 }}>
      <Stack direction="row" sx={{ mb: 1, justifyContent: 'space-between', alignItems: 'center' }}>
        <Typography variant="subtitle1">
          Task: {state.task_id}
        </Typography>
        <Chip
          label={state.status}
          size="small"
          color={
            state.status === 'completed' ? 'success' :
            state.status === 'running' ? 'info' :
            state.status === 'failed' ? 'error' :
            state.status === 'cancelled' ? 'warning' : 'default'
          }
        />
      </Stack>

      <LinearProgress variant="determinate" value={Math.min(pct, 100)} sx={{ height: 10, borderRadius: 1, mb: 1 }} />

      <Stack direction="row" spacing={3} sx={{ flexWrap: 'wrap', gap: 1 }}>
        <Typography variant="body2">Total: {state.total.toLocaleString()}</Typography>
        <Typography variant="body2" color="success.main">OK: {state.completed.toLocaleString()}</Typography>
        {state.skipped > 0 && <Typography variant="body2" color="text.secondary">Skip: {state.skipped.toLocaleString()}</Typography>}
        {state.failed > 0 && <Typography variant="body2" color="error">Fail: {state.failed.toLocaleString()}</Typography>}
        <Typography variant="body2">{state.rate} files/s</Typography>
        <Typography variant="body2">{state.elapsed.toFixed(1)}s</Typography>
      </Stack>

      {!done && (
        <Button variant="outlined" color="warning" size="small" sx={{ mt: 1 }} onClick={handleCancel}>
          Cancel
        </Button>
      )}

      {state.errors.length > 0 && (
        <Alert severity="error" sx={{ mt: 1, maxHeight: 150, overflow: 'auto' }}>
          {state.errors.map((e, i) => <div key={i}>{e}</div>)}
        </Alert>
      )}
    </Paper>
  );
}
