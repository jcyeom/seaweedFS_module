import { Dialog, DialogTitle, DialogContent, IconButton } from '@mui/material';
import CloseIcon from '@mui/icons-material/Close';
import { previewUrl } from '../api/client';

interface Props {
  folder: string;
  filename: string | null;
  onClose: () => void;
}

export default function ImagePreview({ folder, filename, onClose }: Props) {
  if (!filename) return null;

  return (
    <Dialog open maxWidth="md" fullWidth onClose={onClose}>
      <DialogTitle sx={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        {filename}
        <IconButton onClick={onClose}><CloseIcon /></IconButton>
      </DialogTitle>
      <DialogContent sx={{ textAlign: 'center' }}>
        <img
          src={previewUrl(folder, filename)}
          alt={filename}
          style={{ maxWidth: '100%', maxHeight: '70vh', objectFit: 'contain' }}
        />
      </DialogContent>
    </Dialog>
  );
}
