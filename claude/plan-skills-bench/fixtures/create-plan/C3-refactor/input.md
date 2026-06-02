reports.py has grown messy — build_report does fetching, formatting, and exporting all in one
function, and I'm pretty sure there's some dead code and duplication in there too. Can you plan a
refactor to clean it up? I want to keep the behaviour identical. Files: reports.py and utils.py.
