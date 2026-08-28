# fb2cal

Export Facebook birthdays to calendar and contact files.

[![Latest release](https://img.shields.io/github/release/alsd4git/fb2cal.svg?style=flat-square)](https://github.com/alsd4git/fb2cal/releases)
[![Tests](https://img.shields.io/github/actions/workflow/status/alsd4git/fb2cal/test-fb2cal.yml?style=flat-square)](https://github.com/alsd4git/fb2cal/actions)
[![Issues](https://img.shields.io/github/issues/alsd4git/fb2cal.svg?style=flat-square)](https://github.com/alsd4git/fb2cal/issues)
[![License](https://img.shields.io/github/license/alsd4git/fb2cal.svg?style=flat-square)](https://github.com/alsd4git/fb2cal/blob/main/LICENSE)

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

## Quick start

### From a checkout

```bash
git clone https://github.com/alsd4git/fb2cal.git
cd fb2cal
uv sync --dev
uv run fb2cal doctor --cookies ./facebook-cookies.json
uv run fb2cal export --cookies ./facebook-cookies.json \
  --format ics --output ./out/birthdays.ics
```

The `out/` directory is ignored by Git. Keep generated files private because they contain
personal contact data.

### Export formats

```bash
uv run fb2cal export --cookies ./facebook-cookies.json --format ics --output ./out/birthdays.ics
uv run fb2cal export --cookies ./facebook-cookies.json --format json --output ./out/birthdays.json
uv run fb2cal export --cookies ./facebook-cookies.json --format vcf --output ./out/birthdays.vcf
uv run fb2cal export --cookies ./facebook-cookies.json --format vcf \
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
   uv run fb2cal doctor --cookies ./facebook-cookies.json
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

```bash
uv sync --dev
uv run pytest -q
uv run python -m unittest discover tests
uv run ruff format --check fb2cal tests --exclude tests/mocks
uv run ruff check fb2cal tests
uv build
```

The test suite is fully offline and contains no Facebook credentials or personal data.

## Packaging status

This fork is source-first for now. The distribution name `fb2cal` is already published by the
upstream maintainer on [PyPI](https://pypi.org/project/fb2cal/), so publishing this fork under the
same name requires coordination with the upstream owner or a distinct distribution name. Until
that decision is made, install and run the checkout with `uv`.

The CI validates both the test matrix and the source and wheel distributions. Once a release version
and distribution name are agreed, the release workflow can be used with a matching tag. Record
user-visible changes in [CHANGELOG.md](CHANGELOG.md) before creating it:

```bash
uv sync --locked --dev
uv build
git tag -a vX.Y.Z -m "Release vX.Y.Z"
git push origin vX.Y.Z
```

The tag workflow creates a GitHub release with the built artifacts. It does not publish to PyPI
until package ownership and trusted-publishing credentials have been agreed.

## Upstream and contributions

- Fork repository: [alsd4git/fb2cal](https://github.com/alsd4git/fb2cal)
- Original project: [mobeigi/fb2cal](https://github.com/mobeigi/fb2cal)
- Open issues in the original project: [mobeigi/fb2cal/issues](https://github.com/mobeigi/fb2cal/issues)

Please open fork-specific issues and pull requests in this repository. Changes that are small and
compatible with the upstream architecture may later be proposed upstream as focused pull requests.

## License

GNU General Public License v3.0 or later. See [LICENSE](https://github.com/alsd4git/fb2cal/blob/main/LICENSE).
