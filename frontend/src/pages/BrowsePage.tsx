import { useEffect, useState, useCallback } from 'react';
import {
  Box, ToggleButton, ToggleButtonGroup, TextField, Typography,
  CircularProgress, Pagination, Stack,
} from '@mui/material';
import { DataGrid, type GridColDef } from '@mui/x-data-grid';
import CategoryFilter from '../components/CategoryFilter';
import ImagePreview from '../components/ImagePreview';
import { listFiles, getStats } from '../api/client';
import type { FileEntry, CategoryStat } from '../types';

const PAGE_SIZE = 100;

const columns: GridColDef[] = [
  { field: 'name', headerName: 'Filename', flex: 1, minWidth: 400 },
  {
    field: 'size',
    headerName: 'Size',
    width: 120,
    valueFormatter: (value: number) => {
      if (value < 1024) return `${value} B`;
      return `${(value / 1024).toFixed(1)} KB`;
    },
  },
  { field: 'category', headerName: 'Category', width: 120 },
];

export default function BrowsePage() {
  const [folder, setFolder] = useState<string>('accept');
  const [category, setCategory] = useState<string | null>(null);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [files, setFiles] = useState<FileEntry[]>([]);
  const [total, setTotal] = useState(0);
  const [categories, setCategories] = useState<CategoryStat[]>([]);
  const [loading, setLoading] = useState(false);
  const [preview, setPreview] = useState<string | null>(null);

  const fetchStats = useCallback(async (f: string) => {
    try {
      const data = await getStats(f);
      setCategories(data.categories);
    } catch { /* ignore */ }
  }, []);

  const fetchFiles = useCallback(async () => {
    setLoading(true);
    try {
      const data = await listFiles(folder, page, PAGE_SIZE, category || undefined, search || undefined);
      setFiles(data.files);
      setTotal(data.total);
    } catch { /* ignore */ }
    setLoading(false);
  }, [folder, page, category, search]);

  useEffect(() => { fetchStats(folder); }, [folder, fetchStats]);
  useEffect(() => { fetchFiles(); }, [fetchFiles]);

  const handleFolderChange = (_: unknown, val: string | null) => {
    if (val) { setFolder(val); setCategory(null); setSearch(''); setPage(1); }
  };

  const totalPages = Math.ceil(total / PAGE_SIZE);

  return (
    <Box>
      <Typography variant="h5" gutterBottom>Browse Files</Typography>

      <Stack direction="row" spacing={2} sx={{ mb: 2, alignItems: 'center' }}>
        <ToggleButtonGroup value={folder} exclusive onChange={handleFolderChange} size="small">
          <ToggleButton value="accept">Accept</ToggleButton>
          <ToggleButton value="non_accept">Non-Accept</ToggleButton>
        </ToggleButtonGroup>
        <TextField
          size="small" placeholder="Search filename..." value={search}
          onChange={(e) => { setSearch(e.target.value); setPage(1); }}
          sx={{ width: 300 }}
        />
        <Typography variant="body2" color="text.secondary">
          {total.toLocaleString()} files
        </Typography>
      </Stack>

      <CategoryFilter categories={categories} selected={category} onSelect={(c) => { setCategory(c); setPage(1); }} />

      {loading ? (
        <Box sx={{ display: 'flex', justifyContent: 'center', py: 4 }}><CircularProgress /></Box>
      ) : (
        <>
          <DataGrid
            rows={files.map((f, i) => ({ id: i, ...f }))}
            columns={columns}
            hideFooter
            density="compact"
            onRowClick={(params) => setPreview(params.row.name)}
            sx={{ height: 500, cursor: 'pointer' }}
          />
          {totalPages > 1 && (
            <Stack direction="row" sx={{ mt: 2, justifyContent: 'center' }}>
              <Pagination count={totalPages} page={page} onChange={(_, p) => setPage(p)} />
            </Stack>
          )}
        </>
      )}

      <ImagePreview folder={folder} filename={preview} onClose={() => setPreview(null)} />
    </Box>
  );
}
