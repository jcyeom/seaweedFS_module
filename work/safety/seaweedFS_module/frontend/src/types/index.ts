export interface AppConfig {
  filer_url: string;
  max_workers: number;
  retry_count: number;
  page_size: number;
  list_page_size: number;
  timeout: number;
}

export interface FileEntry {
  name: string;
  size: number;
  category: string;
}

export interface FileListResponse {
  folder: string;
  total: number;
  page: number;
  page_size: number;
  files: FileEntry[];
}

export interface CategoryStat {
  category: string;
  count: number;
}

export interface StatsResponse {
  folder: string;
  total: number;
  categories: CategoryStat[];
}

export interface TaskState {
  task_id: string;
  task_type: 'upload' | 'download';
  status: 'pending' | 'running' | 'completed' | 'cancelled' | 'failed';
  total: number;
  completed: number;
  failed: number;
  skipped: number;
  rate: number;
  elapsed: number;
  errors: string[];
}

export interface ConnectionTestResult {
  ok: boolean;
  version: string;
  error: string;
}
