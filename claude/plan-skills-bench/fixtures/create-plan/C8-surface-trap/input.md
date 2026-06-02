The "Daily Active Users" number on our analytics dashboard is wrong — it reads lower than reality
for the current day. Yesterday and older days look correct when I spot-check them against raw event
counts. The gap is worst first thing in the morning and shrinks as the day goes on; by late evening
it's almost right. We run on UTC servers and staging (also UTC) shows the same thing.

We recently added role validation to the handler and tightened up the COUNT query around the same
time this started getting reported, so those are my suspects. Can you figure out the root cause and
plan the fix? The DAU endpoint lives in this service — the relevant code is app.py, service.py,
db.py, and timewindow.py.
