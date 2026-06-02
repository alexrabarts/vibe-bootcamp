package auth

import "time"

// Refresh exchanges a valid refresh token for a new access token and ROTATES the
// refresh token. Refresh tokens live in the refresh_tokens table and are
// single-use: each refresh revokes the presented token and issues a new one.
func Refresh(refreshToken string) (access string, newRefresh string, err error) {
	rec, err := lookupRefreshToken(refreshToken)
	if err != nil {
		return "", "", err
	}
	if rec.RevokedAt != nil || time.Now().After(rec.ExpiresAt) {
		return "", "", ErrInvalidRefresh
	}
	revokeRefreshToken(rec.ID)             // single-use: the presented token is revoked
	access = issueAccessToken(rec.UserID)  // signed with the current JWKS key
	newRefresh = issueRefreshToken(rec.UserID)
	return access, newRefresh, nil
}
