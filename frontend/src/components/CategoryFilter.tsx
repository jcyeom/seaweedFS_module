import { Chip, Stack } from '@mui/material';
import type { CategoryStat } from '../types';

interface Props {
  categories: CategoryStat[];
  selected: string | null;
  onSelect: (cat: string | null) => void;
}

export default function CategoryFilter({ categories, selected, onSelect }: Props) {
  return (
    <Stack direction="row" spacing={1} sx={{ mb: 2, flexWrap: 'wrap', gap: 1 }}>
      <Chip
        label={`All (${categories.reduce((s, c) => s + c.count, 0)})`}
        color={selected === null ? 'primary' : 'default'}
        onClick={() => onSelect(null)}
      />
      {categories.map((c) => (
        <Chip
          key={c.category}
          label={`${c.category} (${c.count.toLocaleString()})`}
          color={selected === c.category ? 'primary' : 'default'}
          onClick={() => onSelect(selected === c.category ? null : c.category)}
        />
      ))}
    </Stack>
  );
}
