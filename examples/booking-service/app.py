#!/usr/bin/env python3
"""Local reference demo, not a measured NULNUL run. Python standard library only."""

import argparse
import json
import sqlite3
from http.server import BaseHTTPRequestHandler, HTTPServer


SLOTS = ("09:00", "10:30", "13:00", "14:30")

PAGE = r'''<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>Open Studio | Book a session</title>
<style>
:root { --ink:#173b45; --muted:#49636a; --paper:#eef5f3; --teal:#075c64; --mist:#d6e9e8; --sun:#e4ad27; }
* { box-sizing:border-box; }
body { margin:0; color:var(--ink); font-family:"Trebuchet MS",Verdana,sans-serif; background:radial-gradient(ellipse at 0 0,var(--mist),transparent 65%),var(--paper); }
header,main,footer { width:min(1080px,calc(100% - 48px)); margin:auto; }
header { display:flex; flex-wrap:wrap; justify-content:space-between; gap:12px; padding:28px 0; border-bottom:1px solid #aac5c7; }
.brand { font-weight:bold; letter-spacing:.07em; }
.tag { font-size:.75rem; letter-spacing:.1em; text-transform:uppercase; }
main { display:grid; grid-template-columns:1fr 1fr; gap:64px; padding:72px 0; align-items:start; }
h1 { font:normal clamp(2.7rem,5.5vw,4.6rem)/1.05 "Palatino Linotype","Book Antiqua",Palatino,serif; letter-spacing:-.04em; margin:20px 0 24px; }
p { line-height:1.65; }
.intro p { max-width:36ch; color:var(--muted); }
.timeline { margin:36px 0 0; padding:20px; border-left:5px solid var(--sun); background:repeating-linear-gradient(transparent 0 31px,#aac5c740 31px 32px); }
.timeline strong { display:block; margin-bottom:10px; }
.timeline span { display:block; line-height:2; font-size:.85rem; }
.card { background:#fff; border:1px solid #aac5c7; border-radius:16px; padding:32px; box-shadow:0 16px 40px #173b4510; animation:arrive .4s ease-out; }
h2 { font:normal 1.9rem "Palatino Linotype","Book Antiqua",Palatino,serif; margin:0 0 8px; }
.note { color:var(--muted); font-size:.85rem; margin:8px 0 24px; }
fieldset { border:0; padding:0; margin:0 0 24px; min-width:0; }
legend,.name-label { font-size:.9rem; font-weight:bold; margin-bottom:12px; display:block; }
.slots { display:grid; grid-template-columns:1fr 1fr; gap:12px; }
.slot { display:flex; gap:10px; align-items:center; padding:16px 10px; border:1px solid #aac5c7; border-radius:8px; cursor:pointer; }
.slot span { display:grid; gap:6px; }
.slot small { color:var(--muted); font-size:.72rem; }
.slot input { accent-color:var(--teal); width:18px; height:18px; flex-shrink:0; }
.slot input:checked + span { color:var(--teal); font-weight:bold; }
.slot.unavailable { background:#edf1f1; cursor:not-allowed; }
.slot.unavailable strong { text-decoration:line-through; }
input[type=text] { width:100%; padding:14px; border:1px solid #7d9da0; border-radius:8px; font:inherit; color:var(--ink); }
button { width:100%; margin-top:22px; padding:16px; border:0; border-radius:8px; font:inherit; font-weight:bold; color:#fff; background:var(--teal); cursor:pointer; }
button:disabled { background:#637b7e; cursor:not-allowed; }
:focus-visible { outline:3px solid var(--sun); outline-offset:4px; }
#status { min-height:3em; margin:18px 0 0; font-size:.9rem; }
footer { border-top:1px solid #aac5c7; padding:22px 0 32px; color:var(--muted); font-size:.8rem; line-height:1.6; }
@keyframes arrive { from { opacity:0; transform:translateY(10px); } to { opacity:1; transform:translateY(0); } }
@media (max-width:760px) { main { grid-template-columns:1fr; gap:32px; padding:36px 0; } .card { padding:24px; } h1 { max-width:14ch; } }
@media (prefers-reduced-motion:reduce) { .card { animation:none; } }
</style>
</head>
<body>
<header><span class="brand">OPEN STUDIO</span><span class="tag">NULNUL in Action / Local reference demo</span></header>
<main>
<section class="intro">
<span class="tag">A little space for your next idea</span>
<h1>Choose a time.<br>Make something.</h1>
<p>Reserve one of four studio sessions. This is a fictional demo day, not a real studio or a calendar connected to an account.</p>
<div class="timeline"><strong>One slot. One booking.</strong><span>The API rejects a second booking for the same time.</span><span>Refresh to see current availability.</span><span>Restart the server to reset the demo.</span></div>
</section>
<section class="card" aria-labelledby="booking-title">
<h2 id="booking-title">Your studio session</h2>
<p class="note">Demo day / 60 minutes per session / No payment</p>
<form id="booking">
<fieldset><legend>Choose an available time</legend><div id="slots" class="slots">Loading times...</div></fieldset>
<label class="name-label" for="name">Fictional guest name</label>
<input id="name" name="name" type="text" maxlength="60" required autocomplete="off" placeholder="Example Guest" aria-describedby="privacy">
<p id="privacy" class="note">Use a made-up name. Nothing is sent to an external service.</p>
<button id="submit" type="submit" disabled>Book this session</button>
<p id="status" role="status" aria-live="polite"></p>
</form>
</section>
</main>
<footer>Reference implementation, not a measured harness success. Local memory only; bookings disappear when this process stops. Not for public hosting.</footer>
<script>
const form = document.querySelector('#booking');
const slots = document.querySelector('#slots');
const status = document.querySelector('#status');
const submit = document.querySelector('#submit');
let ready = false, busy = false;
function updateButton() { submit.disabled = busy || !ready; }
async function loadSlots() {
  ready = false;
  updateButton();
  try {
    const response = await fetch('/api/slots');
    if (!response.ok) throw new Error('Availability could not be loaded. Refresh to try again.');
    const data = await response.json();
    const labels = data.slots.map(slot => {
      const label = document.createElement('label');
      label.className = 'slot' + (slot.available ? '' : ' unavailable');
      const input = document.createElement('input');
      Object.assign(input, {type:'radio', name:'slot', value:slot.time, required:true, disabled:!slot.available});
      const text = document.createElement('span');
      const time = document.createElement('strong');
      time.textContent = slot.time;
      const state = document.createElement('small');
      state.textContent = slot.available ? 'Available' : 'Already booked';
      text.append(time, state);
      label.append(input, text);
      return label;
    });
    slots.replaceChildren(...labels);
    ready = data.slots.some(slot => slot.available);
    if (!ready) status.textContent = 'All demo sessions are booked. Restart the server to reset them.';
  } catch (error) {
    status.textContent = error.message || 'Connection failed. Check that the local server is running.';
  }
  updateButton();
}
form.addEventListener('submit', async event => {
  event.preventDefault();
  if (busy || !ready || !form.reportValidity()) return;
  busy = true;
  updateButton();
  status.textContent = 'Booking your session...';
  try {
    const fields = new FormData(form);
    const response = await fetch('/api/bookings', {
      method:'POST', headers:{'Content-Type':'application/json'},
      body:JSON.stringify({slot:fields.get('slot'), name:fields.get('name')})
    });
    const data = await response.json();
    status.textContent = response.ok
      ? `Booked: ${data.booking.slot} for ${data.booking.name}.`
      : data.error;
    await loadSlots();
  } catch (error) {
    status.textContent = 'Could not confirm the booking. Refresh availability before retrying.';
  } finally {
    busy = false;
    updateButton();
  }
});
loadSlots();
</script>
</body>
</html>'''


def reserve(database, payload):
    if not isinstance(payload, dict) or set(payload) != {"slot", "name"}:
        return 400, {"error": "Send exactly the slot and name fields."}
    slot, name = payload["slot"], payload["name"]
    if not isinstance(slot, str) or slot not in SLOTS:
        return 400, {"error": "Choose one of the listed demo times."}
    if not isinstance(name, str) or not name.isprintable() or not 1 <= len(name.strip()) <= 60:
        return 400, {"error": "Use a fictional name of 1 to 60 printable characters."}
    try:
        database.execute("INSERT INTO bookings (slot, name) VALUES (?, ?)", (slot, name.strip()))
        database.commit()
    except sqlite3.IntegrityError:
        database.rollback()
        return 409, {"error": "That time was just booked. Choose another available session."}
    return 201, {"booking": {"slot": slot, "name": name.strip()}}


class Handler(BaseHTTPRequestHandler):
    def setup(self):
        super().setup()
        self.connection.settimeout(5)

    def log_message(self, format, *args):
        pass

    def reply(self, status, payload, html=False):
        body = payload.encode("utf-8") if html else json.dumps(payload).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "text/html; charset=utf-8" if html else "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.send_header("Cache-Control", "no-store")
        self.send_header("X-Content-Type-Options", "nosniff")
        self.send_header("Content-Security-Policy", "default-src 'self'; script-src 'unsafe-inline'; style-src 'unsafe-inline'; base-uri 'none'; frame-ancestors 'none'; form-action 'self'")
        self.end_headers()
        self.wfile.write(body)

    def local_request(self):
        host = self.headers.get("Host", "")
        allowed = {f"127.0.0.1:{self.server.server_port}", f"localhost:{self.server.server_port}"}
        origin = self.headers.get("Origin")
        if host not in allowed or (origin is not None and origin != "http://" + host):
            self.reply(403, {"error": "Use the local demo origin."})
            return False
        return True

    def do_GET(self):
        if not self.local_request():
            return
        path = self.path.split("?", 1)[0]
        if path == "/":
            self.reply(200, PAGE, html=True)
        elif path == "/api/slots":
            booked = {row[0] for row in self.server.database.execute("SELECT slot FROM bookings")}
            self.reply(200, {"slots": [{"time": slot, "available": slot not in booked} for slot in SLOTS]})
        else:
            self.reply(404, {"error": "Not found."})

    def do_POST(self):
        if not self.local_request():
            return
        if self.path != "/api/bookings":
            self.reply(404, {"error": "Not found."})
            return
        if self.headers.get("Content-Type", "").split(";", 1)[0].strip().lower() != "application/json":
            self.reply(415, {"error": "Use application/json."})
            return
        length = self.headers.get("Content-Length", "")
        if self.headers.get("Transfer-Encoding") or not length.isascii() or not length.isdecimal():
            self.reply(400, {"error": "Send a Content-Length without transfer encoding."})
            return
        if len(length) > 4 or not 0 < int(length) <= 4096:
            self.reply(413, {"error": "Send a JSON body between 1 and 4096 bytes."})
            return
        try:
            payload = json.loads(self.rfile.read(int(length)))
        except (ValueError, UnicodeError):
            self.reply(400, {"error": "Send valid UTF-8 JSON."})
            return
        status, result = reserve(self.server.database, payload)
        self.reply(status, result)


def make_server(port):
    server = HTTPServer(("127.0.0.1", port), Handler)
    # ponytail: one synchronous writer and ephemeral data; use persistent storage
    # and authentication before considering shared or production use.
    server.database = sqlite3.connect(":memory:", check_same_thread=False)
    server.database.execute("CREATE TABLE bookings (slot TEXT PRIMARY KEY, name TEXT NOT NULL)")
    return server


def check():
    """Exercise the HTTP contract and rejection paths, not browser behavior."""
    from threading import Thread
    from urllib.error import HTTPError
    from urllib.request import Request, urlopen

    server = make_server(0)
    thread = Thread(target=server.serve_forever, daemon=True)
    thread.start()
    base = f"http://127.0.0.1:{server.server_port}"

    def request(path, payload=None, headers=None):
        body = payload if isinstance(payload, bytes) else json.dumps(payload).encode() if payload is not None else None
        options = {"Content-Type": "application/json", **(headers or {})}
        try:
            response = urlopen(Request(base + path, data=body, headers=options), timeout=3)
        except HTTPError as error:
            response = error
        with response:
            return response.status, json.load(response)

    try:
        with urlopen(base, timeout=3) as response:
            assert response.status == 200 and b'id="booking"' in response.read()
        status, before = request("/api/slots")
        assert status == 200 and len(before["slots"]) == 4
        assert all(slot["available"] for slot in before["slots"])
        status, created = request("/api/bookings", {"slot": "09:00", "name": "Example Guest"})
        assert status == 201 and created["booking"]["slot"] == "09:00"
        assert request("/api/bookings", {"slot": "09:00", "name": "Another Guest"})[0] == 409
        for payload in ({"slot": "25:00", "name": "Example"}, {"slot": "10:30", "name": " "},
                        {"slot": "10:30", "name": 7}, {"slot": "10:30", "guest": "Wrong field"},
                        {"slot": ["10:30"], "name": "Example"}, [], b"{broken"):
            assert request("/api/bookings", payload)[0] == 400
        valid = {"slot": "10:30", "name": "Example"}
        assert request("/api/bookings", valid, {"Content-Type": "text/plain"})[0] == 415
        assert request("/api/bookings", valid, {"Origin": "https://example.invalid"})[0] == 403
        assert request("/api/slots", headers={"Host": "example.invalid"})[0] == 403
        assert request("/missing")[0] == 404
        status, after = request("/api/slots")
        assert status == 200 and after["slots"] == [
            {"time": slot, "available": slot != "09:00"} for slot in SLOTS
        ]
        print("PASS: UI response, availability, booking, conflict, invalid input, and local-origin checks.")
    finally:
        server.shutdown()
        thread.join()
        server.server_close()
        server.database.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--port", type=int, default=8765)
    parser.add_argument("--check", action="store_true", help="run the bounded HTTP self-check")
    args = parser.parse_args()
    if args.check:
        check()
        return
    if not 0 <= args.port <= 65535:
        parser.error("port must be between 0 and 65535")
    server = make_server(args.port)
    print(f"Open http://127.0.0.1:{server.server_port} (fictional data; Ctrl+C resets bookings)", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
        server.database.close()


if __name__ == "__main__":
    main()
