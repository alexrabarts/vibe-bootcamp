"use client";

import { useState } from "react";

export type Filters = {
  status?: string;
  owner?: string;
  from?: string;
  to?: string;
};

// Filters live in component state only: they reset on reload and do not sync
// across devices. There is no "save this filter set" affordance yet.
export function FilterBar({ onChange }: { onChange: (f: Filters) => void }) {
  const [filters, setFilters] = useState<Filters>({});

  function update(patch: Partial<Filters>) {
    const next = { ...filters, ...patch };
    setFilters(next);
    onChange(next);
  }

  return (
    <div className="filter-bar">
      {/* status / owner / date inputs call update(...) */}
    </div>
  );
}
