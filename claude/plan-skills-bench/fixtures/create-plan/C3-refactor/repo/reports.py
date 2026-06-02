"""Monthly revenue report builder."""

import csv
import io
import json
import datetime  # unused

from utils import format_currency


# TODO: remove legacy_export once everyone is on v2 (migration finished 2024-01)
def legacy_export(rows):
    # Dead code: nothing calls this anymore.
    out = io.StringIO()
    w = csv.writer(out)
    for r in rows:
        w.writerow([r["month"], r["revenue"]])
    return out.getvalue()


def build_report(db, account_id, fmt):
    # Fetch
    rows = db.query(
        "SELECT month, revenue, currency FROM monthly_revenue WHERE account_id = ?",
        [account_id],
    )

    # Transform + format (currency formatting duplicated from utils.format_currency)
    formatted = []
    for r in rows:
        symbol = "$" if r["currency"] == "USD" else r["currency"] + " "
        amount = f"{symbol}{r['revenue']:,.2f}"
        formatted.append({"month": r["month"], "revenue": amount})

    # Export
    if fmt == "csv":
        out = io.StringIO()
        w = csv.writer(out)
        for r in formatted:
            w.writerow([r["month"], r["revenue"]])
        return out.getvalue()
    elif fmt == "json":
        return json.dumps(formatted)
    else:
        # if fmt == "pdf":
        #     return render_pdf(formatted)
        raise ValueError("unsupported format")
