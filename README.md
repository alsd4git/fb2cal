<p align="center">
<img src="https://i.imgur.com/ToHPLjD.png" height="110px" width="auto"/>
<br/>
<h3 align="center">fb2cal</h3>
<p align="center">Facebook Birthday Events to ICS file converter</p>
<h2></h2>
</p>
<br />

<p align="center">
<a href="../../releases"><img src="https://img.shields.io/github/release/mobeigi/fb2cal.svg?style=flat-square" /></a>
<a href="../../actions"><img src="https://img.shields.io/github/actions/workflow/status/mobeigi/fb2cal/test-fb2cal.yml?style=flat-square" /></a>
<a href="../../issues"><img src="https://img.shields.io/github/issues/mobeigi/fb2cal.svg?style=flat-square" /></a>
<a href="../../pulls"><img src="https://img.shields.io/github/issues-pr/mobeigi/fb2cal.svg?style=flat-square" /></a> 
<a href="LICENSE.md"><img src="https://img.shields.io/github/license/mobeigi/fb2cal.svg?style=flat-square" /></a>
</p>

## Description
Around 20 June 2019, Facebook removed their Facebook Birthday ICS export option.  
This change was unannounced and no reason was ever released.  

fb2cal is a tool which restores this functionality.  
It works by calling endpoints that power the https://www.facebook.com/events/birthdays/ page.  
After gathering a list of birthdays for all the users friends for a full year, it creates a ICS calendar file. This ICS file can then be imported into third party tools (such as Google Calendar or Apple Calendar).

## Caveats
* Facebook accounts secured with 2FA are currently not supported (see [#9](../../issues/9))
* During Facebook authentication, a security checkpoint may trigger that will force you to change your Facebook password.

## Requirements
* Facebook account
* Python 3.10+
* [uv](https://docs.astral.sh/uv/)
* Scheduler tool to automatically run script periodically (optional)

## PyPI Project
https://pypi.org/project/fb2cal/

## Instructions

### Installed package
1. Install the published package with uv:
`uv tool install fb2cal`
2. Export a browser session cookie JSON and validate it:
`fb2cal doctor --cookies ./facebook-cookies.json`
3. Export the calendar:
`fb2cal export --cookies ./facebook-cookies.json --format ics --output ./out/birthdays.ics`

### Local
1. Clone repo  
`git clone git@github.com:mobeigi/fb2cal.git`
2. Copy `config/config-template.ini` to `config/config.ini`.
3. Create the uv environment:
`uv sync --dev`
4. Export a browser session cookie JSON and run:
`uv run fb2cal export --cookies ./facebook-cookies.json --format json --output ./out/birthdays.json`
5. Check the output folder (`out` by default) for the created file.

Every full export prints a recap on stderr, leaving JSON/VCF/ICS stdout clean when no
`--output` is supplied:

```text
Recap estrazione:
  amici con compleanno visibile: 621
  compleanni con anno: 493
  compleanni senza anno: 128
  totale amici del profilo: non disponibile nella birthday query
```

The JSON export also stores these counts under its top-level `summary` field.
All exported formats contain personal contact data; store them with permissions appropriate for
your machine and do not commit them.

The profile-wide friend total is intentionally not fetched by a second request. The birthday
GraphQL response does not contain that aggregate, while Meta's platform APIs do not expose a
personal user's complete friend list/count to a normal app integration; they are restricted to
friends who also use the app. A profile-page scrape would therefore be an undocumented,
locale-dependent fallback that could silently report a different number. The recap keeps this
value explicit as “non disponibile” instead of adding a fragile network call.

## Configuration
This tool can be configured by editing the `config/config.ini` configuration file. Cookie/session
authentication is preferred; email/password remains only for legacy compatibility.

<table> <thead> <tr> <th>Section</th> <th>Key</th> <th>Valid Values</th> <th>Description</th> </tr></thead> <tbody> <tr> <td rowspan=3>AUTH</td><td>cookies_file</td><td>JSON path</td><td>Explicit browser cookie export (recommended)</td></tr><tr> <td>fb_email</td><td></td><td>Legacy login email</td></tr><tr> <td>fb_pass</td><td></td><td>Legacy login password</td></tr><tr> <td rowspan=2>FILESYSTEM</td><td>save_to_file</td><td>True, False</td><td>If tool should save ICS file to the local file system</td></tr><tr> <td>ics_file_path</td><td></td><td>Path to save ICS file to (including file name)</td></tr><tr> <td>LOGGING</td><td>level</td><td>DEBUG, INFO, WARNING, ERROR, CRITICAL</td><td>Logging level to use. Default: INFO</td></tr></tbody></table>

### Exporting a session cookie file safely

The program never scans Chrome/Firefox profiles or decrypts browser databases. Export the
cookies explicitly from a browser session where Facebook is already logged in, then treat the
file like a password:

1. Open `https://www.facebook.com/events/birthdays/` and confirm the page works.
2. Use a trusted cookie-export tool or browser developer tools to export the complete
   `facebook.com` cookie jar as JSON. It must include at least `c_user`; keep all other cookies.
   On Chrome, one practical option is [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm): open it on the Facebook tab, export only the current site as JSON, then remove the extension when finished. A JavaScript snippet alone cannot export `HttpOnly` cookies.
   The accepted shape is a browser-style list such as:
   ```json
   [{"name":"c_user","value":"<REDACTED>","domain":".facebook.com","path":"/","secure":true}]
   ```
3. Save it outside Git, restrict it (`chmod 600 facebook-cookies.json`), and never paste its
   contents into chat, issues, logs, or screenshots.
4. Verify locally without generating an ICS file:
   `uv run fb2cal doctor --cookies ./facebook-cookies.json`
5. Export the desired format:
   `uv run fb2cal export --cookies ./facebook-cookies.json --format json --output ./out/birthdays.json`
   Use `--format ics` for the legacy calendar or `--format vcf` for contact import.

If `doctor` reports an expired session or checkpoint, log in interactively again and export a
fresh file. Cookies are bearer credentials; revoke the browser session in Facebook if a cookie
file is accidentally disclosed.

## Upstream issue mapping

The original repository currently lists five open issues: [#129](https://github.com/mobeigi/fb2cal/issues/129),
[#109](https://github.com/mobeigi/fb2cal/issues/109), [#48](https://github.com/mobeigi/fb2cal/issues/48),
[#15](https://github.com/mobeigi/fb2cal/issues/15), and [#9](https://github.com/mobeigi/fb2cal/issues/9).

This fork addresses them as follows:

| Issue | Fork status |
| --- | --- |
| #129 login broken | Mitigated by explicit browser-session cookies, `doctor`, typed auth errors, and a retained legacy backend. |
| #9 2FA | No automated 2FA or checkpoint bypass; an interactively authenticated browser session works. |
| #48 password handling | Passwords are no longer required in the recommended flow and are never persisted by the new CLI. |
| #109 leap years | Fixed in ICS export, including unknown-year February 29, with regression tests. |
| #15 one-click installation | Improved with a `uv` workflow and `fb2cal` console entry point; OS-specific packaged installers remain future work. |

The remaining roadmap items are intentionally separate projects: direct Google/iCloud/CardDAV
sync, fuzzy contact matching, automatic browser-cookie discovery, and a fully interactive browser
authentication flow.

## Scheduled Task Frequency
It is recommended to run the script **once every 24 hours** to update the ICS file to ensure it is synchronized with the latest Facebook changes (due to friend addition/removal) and to respect the privacy of users who decide to hide their birthday later on. Facebook originally recommended polling for birthday updates **once every 12 hours** based on the `X-PUBLISHED-TTL:PT12H` header included in their ICS files.

## Testing
1. Install the locked development environment:
`uv sync --dev`
2. Run the test suite:
`uv run pytest -q`
3. Run the standard-library test runner as a compatibility check:
`uv run python -m unittest discover tests`
4. Run the linter:
`uv run ruff check fb2cal tests`
5. Build the package:
`uv build`

The suite is fully offline and contains no Facebook credentials or personal data. It can also be
run with `pytest -q`.

## Troubleshooting
If you encounter any issues, please open the `config/config.ini` configuration file and set the `LOGGING` `level` to `DEBUG` (it is `INFO` by default). Include these logs when asking for help.

## Contributions
Contributions are always welcome!
Just make a [pull request](../../pulls).

## Licence
GNU General Public License v3.0
