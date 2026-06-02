export async function fetchDashboard(id: string) {
  const res = await fetch(`/api/dashboards?id=${encodeURIComponent(id)}`);
  if (!res.ok) throw new Error("failed to load dashboard");
  return res.json();
}

// No client methods for saved filters yet.
