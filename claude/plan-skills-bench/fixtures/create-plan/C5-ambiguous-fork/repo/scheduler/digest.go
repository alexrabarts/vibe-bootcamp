package scheduler

import "time"

// nextSendTime returns when the next digest should be sent, given the current
// time and the user's configured send weekday and hour.
//
// It builds the candidate time in now.Location() — the SERVER timezone (UTC in
// production) — and never consults the user's timezone. So a user who configured
// "Monday 09:00" receives the digest at 09:00 server-time on the server's Monday,
// not their own local Monday morning.
func nextSendTime(now time.Time, weekday time.Weekday, hour int) time.Time {
	candidate := time.Date(now.Year(), now.Month(), now.Day(), hour, 0, 0, 0, now.Location())
	for candidate.Weekday() != weekday || !candidate.After(now) {
		candidate = candidate.AddDate(0, 0, 1)
	}
	return candidate
}
