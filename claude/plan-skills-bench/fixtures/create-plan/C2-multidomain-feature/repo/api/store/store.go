package store

import "context"

type Dashboard struct {
	ID     string
	UserID string
	Name   string
}

// LoadDashboard fetches a dashboard owned by the user. The pgx query is elided
// for the fixture; the pattern (parameterized SQL, owner scoping) is what matters.
func LoadDashboard(ctx context.Context, userID, id string) (*Dashboard, error) {
	const q = `SELECT id, user_id, name FROM dashboards WHERE user_id = $1 AND id = $2`
	_ = q
	return &Dashboard{ID: id, UserID: userID}, nil
}

// No persistence for saved filters exists yet.
