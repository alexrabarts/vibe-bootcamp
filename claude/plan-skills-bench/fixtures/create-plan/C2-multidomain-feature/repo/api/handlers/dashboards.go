package handlers

import (
	"net/http"

	"example.com/app/api/store"
)

// GetDashboard returns a dashboard. Filter state is NOT persisted today — it
// lives only in the client (see web/components/FilterBar.tsx).
func GetDashboard(w http.ResponseWriter, r *http.Request) {
	userID := r.Context().Value("user_id").(string)
	dash, err := store.LoadDashboard(r.Context(), userID, r.URL.Query().Get("id"))
	if err != nil {
		http.Error(w, err.Error(), http.StatusInternalServerError)
		return
	}
	writeJSON(w, dash)
}

// There are no handlers for saved filters yet.
