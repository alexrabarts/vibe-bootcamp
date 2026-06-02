package auth

import "net/http"

// RequireAuth validates the access token on every request. On a valid-but-expired
// access token it does NOT refresh inline — it returns 401, and the client is
// expected to call /auth/refresh and retry.
func RequireAuth(next http.Handler) http.Handler {
	return http.HandlerFunc(func(w http.ResponseWriter, r *http.Request) {
		tok := bearerToken(r)
		claims, err := verifyAccessToken(tok)
		if err != nil {
			http.Error(w, "unauthorized", http.StatusUnauthorized)
			return
		}
		r = r.WithContext(withClaims(r.Context(), claims))
		next.ServeHTTP(w, r)
	})
}
