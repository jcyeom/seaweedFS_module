import axios from 'axios';
import type { AppConfig, FileListResponse, StatsResponse, ConnectionTestResult } from '../types';

const api = axios.create({ baseURL: '/api' });

// Settings
export const getSettings = () => api.get<AppConfig>('/settings').then(r => r.data);
export const updateSettings = (data: Partial<AppConfig>) => api.put<AppConfig>('/settings', data).then(r => r.data);
export const testConnection = () => api.get<ConnectionTestResult>('/settings/test').then(r => r.data);

// Browse
export const listFiles = (folder: string, page: number, pageSize: number, category?: string, search?: string) =>
  api.get<FileListResponse>(`/browse/${folder}`, { params: { page, page_size: pageSize, category, search } }).then(r => r.data);

export const getStats = (folder: string) =>
  api.get<StatsResponse>(`/browse/${folder}/stats`).then(r => r.data);

export const previewUrl = (folder: string, filename: string) =>
  `/api/browse/${folder}/preview/${encodeURIComponent(filename)}`;

// Upload
export const startUpload = (localDir: string, remoteDir: string, pattern: string) =>
  api.post<{ task_id: string }>('/upload/start', { local_dir: localDir, remote_dir: remoteDir, pattern }).then(r => r.data);

export const cancelTask = (type: 'upload' | 'download', taskId: string) =>
  api.post(`/${type}/${taskId}/cancel`);

// Download
export const startDownload = (remoteDir: string, localDir: string, category?: string, skipExisting = true) =>
  api.post<{ task_id: string; file_count: number }>('/download/start', {
    remote_dir: remoteDir, local_dir: localDir, category: category || null, skip_existing: skipExisting,
  }).then(r => r.data);
