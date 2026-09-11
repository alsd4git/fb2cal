# fb2cal

Export Facebook birthdays to calendar and contact files.

[![CI](https://github.com/alsd4git/fb2cal/actions/workflows/test-fb2cal.yml/badge.svg)](https://github.com/alsd4git/fb2cal/actions/workflows/test-fb2cal.yml)
[![Latest release](https://img.shields.io/github/v/release/alsd4git/fb2cal)](https://github.com/alsd4git/fb2cal/releases)
[![License: GPL-3.0](https://img.shields.io/badge/license-GPL--3.0-blue.svg)](LICENSE)

This repository is a maintained fork of [mobeigi/fb2cal](https://github.com/mobeigi/fb2cal).
The upstream project is preserved as a reference and as a possible source of focused upstream
contributions.

## What it does

Facebook no longer provides the original birthday calendar export. fb2cal reads the authenticated
birthday page session and queries the same birthday data used by Facebook's web interface. It
deduplicates the visible birthdays for a full year and exports them as:

- ICS calendar events for Google Calendar, Apple Calendar, and similar clients;
- JSON contact data for automation and inspection;
- vCard 4.0 contacts for address-book imports, with a vCard 3.0 compatibility mode for older
  clients.

The export includes only birthdays visible to the authenticated Facebook account. A total profile
friend count is not available in the birthday query and is intentionally not fetched through a
fragile profile-page scrape.

## Requirements

- An authenticated Facebook account;
- Python 3.10 or newer;
- [uv](https://docs.astral.sh/uv/).

The command never scans browser profiles or decrypts browser databases. It requires an explicit
JSON export of the cookies from a browser session that is already logged in to Facebook.

## Installation

Install the exact wheel published with the tagged GitHub Release:

```bash
uv tool install https://github.com/alsd4git/fb2cal/releases/download/v2.0.0/fb2cal-2.0.0-py3-none-any.whl
fb2cal --help
```

For a one-off run without keeping the tool installed:

```bash
uvx --from https://github.com/alsd4git/fb2cal/releases/download/v2.0.0/fb2cal-2.0.0-py3-none-any.whl fb2cal --help
```

`pip` can install the same wheel when preferred:

```bash
python -m pip install https://github.com/alsd4git/fb2cal/releases/download/v2.0.0/fb2cal-2.0.0-py3-none-any.whl
```

The examples are intentionally pinned to a concrete release so the installed artifact is
reproducible. Replace `v2.0.0` and the wheel filename together when selecting another version.

## Quick start

Validate an exported browser session:

```bash
fb2cal doctor --cookies ./facebook-cookies.json
```

Export birthdays to an ICS calendar:

```bash
fb2cal export --cookies ./facebook-cookies.json \
  --format ics --output ./out/birthdays.ics
```

The `out/` directory is ignored by Git when working from a checkout. Keep generated files private
because they contain personal contact data.

### Export formats

```bash
fb2cal export --cookies ./facebook-cookies.json --format ics --output ./out/birthdays.ics
fb2cal export --cookies ./facebook-cookies.json --format json --output ./out/birthdays.json
fb2cal export --cookies ./facebook-cookies.json --format vcf --output ./out/birthdays.vcf
fb2cal export --cookies ./facebook-cookies.json --format vcf \
  --vcard-version 3.0 --output ./out/birthdays-v3.vcf
```

Without `--output`, the selected format is written to stdout. The extraction summary is always
written to stderr, so exported JSON, VCF, and ICS remain machine-readable:

```text
Extraction summary:
  friends with visible birthdays: 621
  birthdays with year: 493
  birthdays without year: 128
  total profile friends: unavailable from the birthday query
```

The JSON export contains the same counts under its top-level `summary` object.

The VCF export uses vCard 4.0 by default. Dates use the standards-defined basic format, including
`--MMDD` when Facebook exposes a birthday without a year. Use `--vcard-version 3.0` only for
address-book clients that do not support vCard 4.0; that legacy format keeps the older hyphenated
date representation and may be less interoperable for yearless birthdays.

## Exporting Chrome cookies safely

Treat the exported file as a password: cookies are bearer credentials.

1. Open `https://www.facebook.com/events/birthdays/` in Chrome and confirm that the page works.
2. Use a trusted cookie-export tool to export the complete `facebook.com` cookie jar as JSON. On
   Chrome, [Cookie-Editor](https://chromewebstore.google.com/detail/cookie-editor/hlkenndednhfkekhgcdicdfddnkalmdm)
   can export the current site's cookies. Remove the extension when finished. A JavaScript snippet
   cannot export `HttpOnly` cookies.
3. Save the file outside Git, restrict it with `chmod 600 facebook-cookies.json`, and never paste
   its contents into chat, issues, logs, or screenshots. The file must include `c_user` and all
   other Facebook session cookies.
4. Validate the session without writing an export:

   ```bash
   fb2cal doctor --cookies ./facebook-cookies.json
   ```

5. If the session expires, authenticate in Chrome again and export a fresh file.

## Command reference

```text
fb2cal doctor --cookies PATH [--json] [--log-level LEVEL]
fb2cal export --cookies PATH [--format ics|json|vcf] [--vcard-version 4.0|3.0] [--output PATH] [--log-level LEVEL]
```

`--log-level` accepts `DEBUG`, `INFO`, `WARNING`, `ERROR`, or `CRITICAL`. The browser session is
always supplied explicitly; email/password login and automatic browser-cookie discovery are not
part of this fork.

## Scheduling

Run the export once every 24 hours with the scheduler available on your operating system. This
keeps the calendar current when friends are added or removed and respects later birthday privacy
changes. The generated ICS file advertises a twelve-hour publication TTL.

## Development

For source development, use a checkout instead of the installed Release artifact:

```bash
git clone https://github.com/alsd4git/fb2cal.git
cd fb2cal
uv sync --locked --dev
uv run fb2cal --help
uv run pytest -q
uv run python -m unittest discover tests
uv run ruff format --check fb2cal tests --exclude tests/mocks
uv run ruff check fb2cal tests
uv build
```

The test suite is fully offline and contains no Facebook credentials or personal data.

## Packaging and releases

This fork publishes wheel and source distributions through tagged GitHub Releases. It intentionally
does not publish the fork as `fb2cal` on PyPI because that distribution name belongs to the upstream
maintainer.

CI validates both the test matrix and the built distributions. To prepare a new release, record
user-visible changes in [CHANGELOG.md](CHANGELOG.md), update the project version, verify the build,
and push a matching tag:

```bash
uv sync --locked --dev
uv build
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

The tag workflow creates a GitHub Release with wheel and sdist artifacts. No PyPI credentials are
required.

## Upstream and contributions

- Fork repository: [alsd4git/fb2cal](https://github.com/alsd4git/fb2cal)
- Original project: [mobeigi/fb2cal](https://github.com/mobeigi/fb2cal)
- Open issues in the original project: [mobeigi/fb2cal/issues](https://github.com/mobeigi/fb2cal/issues)

Fork-specific pull requests can be opened in this repository. Issues are currently disabled on the
fork; changes that are small and compatible with the upstream architecture may later be proposed
upstream as focused pull requests.

## License

GNU General Public License v3.0 or later. See [LICENSE](https://github.com/alsd4git/fb2cal/blob/main/LICENSE).
