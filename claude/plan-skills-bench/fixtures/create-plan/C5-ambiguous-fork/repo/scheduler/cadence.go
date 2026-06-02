package scheduler

import "time"

// Cadence describes how often a digest is sent. Note: the product/UI calls these
// "reports"; the code calls them "digests".
type Cadence string

const (
	CadenceWeekly  Cadence = "weekly"
	CadenceDaily   Cadence = "daily"
	CadenceMonthly Cadence = "monthly"
)

// UserSchedule is stored per user. SendWeekday and SendHour are interpreted by
// nextSendTime in the server timezone (see digest.go) — the user's Timezone field
// is recorded but currently unused when scheduling.
type UserSchedule struct {
	UserID      string
	Cadence     Cadence
	SendWeekday time.Weekday
	SendHour    int
	Timezone    string // e.g. "America/New_York" — stored but not used by nextSendTime
}

// allCadences share nextSendTime; daily and monthly compute their own next
// occurrence but route through the same server-timezone logic.
