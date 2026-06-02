export async function getJSON(path: string) {
  const res = await fetch(path);
  if (!res.ok) throw new Error(`request failed: ${path}`);
  return res.json();
}

// Add a helper for /api/health/summary here (frontend work item).
