package auth

// verifyAccessToken validates an access token's signature against the JWKS key
// set, which is fetched from the identity provider and cached for 10 minutes.
// Access tokens are short-lived (~15 min); the JWKS cache TTL is what lets key
// rotation propagate — a rotated signing key is picked up on the next refresh of
// the cache.
func verifyAccessToken(tok string) (*Claims, error) {
	key, err := jwksCache.keyFor(tok) // refetches the JWKS if the cache is stale (>10m)
	if err != nil {
		return nil, err
	}
	return parseAndVerify(tok, key)
}
