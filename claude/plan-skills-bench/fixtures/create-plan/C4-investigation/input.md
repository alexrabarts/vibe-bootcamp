Before we touch anything, I want to understand how our auth token refresh flow works end to end —
how access tokens get validated, when and how refresh happens, and how key rotation fits into it.
Can you investigate and explain it? The code is in auth/middleware.go, auth/refresh.go, and
auth/jwks.go. Please don't propose changes yet — I just want to understand how it works today.
