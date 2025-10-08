#!/usr/bin/env python3
# generate_hull_calendar.py
# Simple ICS generator for Hull events. By default it produces sample events.
# Edit or add fetch_* functions to pull real events from websites.

import datetime
import uuid
import logging
from dateutil import parser as dateparser

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")

# -------- CONFIG: Edit these URLs if you want real scrapers later ----------
SOURCES = {
    "whatsonhull": "https://whatsonhull.com/",               # example
    "connexin": "https://connexinlivehull.com/whats-on/",
    "vue": "https://www.myvue.com/cinema/hull-princes-quay/whats-on",
    "odeon": "https://www.odeon.co.uk/cinemas/hull/"
}
# ------------------------------------------------------------------------

def sample_events():
    """Return a few sample events so the pipeline is working immediately."""
    now = datetime.date.today()
    return [
        {
            "summary": "Jimmy Carr: Laughs Funny",
            "location": "Connexin Live, Hull",
            "start": datetime.datetime(now.year, now.month, min(now.day+10,28), 19, 30),
            "description": "Connexin Live show — check tickets."
        },
        {
            "summary": "Wicked — Opening Weekend (sample)",
            "location": "Vue Hull Princes Quay",
            "start": datetime.date.today() + datetime.timedelta(days=30),  # all-day date
            "description": "Cinema opening (sample entry)"
        },
        {
            "summary": "Dune: Part Two — Sample",
            "location": "Odeon Luxe Hull",
            "start": datetime.date.today() + datetime.timedelta(days=15),
            "description": "Sample cinema entry"
        },
    ]

# ----------------- Helpers -----------------
def _escape(text: str) -> str:
    if not text:
        return ""
    return text.replace("\\", "\\\\").replace("\n", "\\n").replace(",", "\\,").replace(";", "\\;")

def format_dt(dt):
    """Return ICS timestamp string in UTC (YYYYMMDDTHHMMSSZ) or YMD for date-only."""
    if isinstance(dt, datetime.date) and not isinstance(dt, datetime.datetime):
        return dt.strftime("%Y%m%d"), True
    # assume datetime
    # make naive datetimes into UTC by treating them as local naive -> convert to UTC naive representation
    if dt.tzinfo is None:
        # treat as local naive; format as UTC timestamp by assuming it's local time
        dt_utc = dt.astimezone(datetime.timezone.utc) if hasattr(dt, "astimezone") else dt
    else:
        dt_utc = dt.astimezone(datetime.timezone.utc)
    return dt_utc.strftime("%Y%m%dT%H%M%SZ"), False

def build_ics(events):
    lines = [
        "BEGIN:VCALENDAR",
        "VERSION:2.0",
        "CALSCALE:GREGORIAN",
        "METHOD:PUBLISH",
        "PRODID:-//Hull Events & Cinema//EN"
    ]
    nowstamp = datetime.datetime.utcnow().strftime("%Y%m%dT%H%M%SZ")
    for ev in events:
        try:
            uid = ev.get("uid") or str(uuid.uuid4())
            summary = _escape(ev.get("summary","No title"))
            location = _escape(ev.get("location",""))
            description = _escape(ev.get("description",""))
            start = ev.get("start")
            if not start:
                logging.warning("Skipping event without start: %s", summary)
                continue
            dtstr, is_date_only = format_dt(start)
            lines.append("BEGIN:VEVENT")
            lines.append(f"UID:{uid}")
            lines.append(f"DTSTAMP:{nowstamp}")
            if is_date_only:
                lines.append(f"DTSTART;VALUE=DATE:{dtstr}")
            else:
                lines.append(f"DTSTART:{dtstr}")
            # Optional end: if duration provided, else skip
            if ev.get("end"):
                endstr, end_is_date = format_dt(ev["end"])
                if end_is_date:
                    lines.append(f"DTEND;VALUE=DATE:{endstr}")
                else:
                    lines.append(f"DTEND:{endstr}")
            lines.append(f"SUMMARY:{summary}")
            if location:
                lines.append(f"LOCATION:{location}")
            if description:
                lines.append(f"DESCRIPTION:{description}")
            lines.append("END:VEVENT")
        except Exception as ex:
            logging.exception("Failed writing event %s: %s", ev.get("summary"), ex)
    lines.append("END:VCALENDAR")
    return "\r\n".join(lines)

def fetch_real_events_placeholder():
    """
    Replace this function with real scrapers.
    For now we return sample events so the ICS is non-empty.
    """
    return sample_events()

def main():
    logging.info("Generating hull_events.ics (3-month window)...")
    events = fetch_real_events_placeholder()
    ics_text = build_ics(events)
    with open("hull_events.ics", "w", encoding="utf-8") as f:
        f.write(ics_text)
    logging.info("Written hull_events.ics with %d events", len(events))

if __name__ == "__main__":
    main()
