#!/usr/bin/env python3
"""Command-line entry point for fb2cal."""

from __future__ import annotations

import argparse
import json
import logging
import sys

from .config import Config
from .errors import (
    AuthenticationError,
    ConfigurationError,
    CookieFileError,
    FacebookError,
    GraphQLQueryError,
    GraphQLSchemaError,
    TokenExtractionError,
)
from .facebook_browser import FacebookBrowser
from .facebook_client import FacebookClient
from .facebook_session import FacebookSession
from .ics_writer import ICSWriter
from .json_exporter import JSONExporter
from .logger import Logger
from .pipeline import extract_birthdays, summarize_contacts
from .transformer import Transformer
from .utils import strtobool
from .vcard_exporter import VCardExporter


def build_parser():
    parser = argparse.ArgumentParser(prog="fb2cal", description="Export Facebook birthdays")
    subparsers = parser.add_subparsers(dest="command")
    export = subparsers.add_parser("export", help="fetch birthdays and export them")
    _add_auth_args(export)
    export.add_argument("--format", choices=("ics", "json", "vcf"), default="ics")
    export.add_argument("--output", help="output path; omit to write the selected format to stdout")
    doctor = subparsers.add_parser("doctor", help="validate auth, token, query, and response schema")
    _add_auth_args(doctor)
    doctor.add_argument("--json", action="store_true", help="emit machine-readable diagnostics")
    return parser


def _add_auth_args(parser):
    parser.add_argument("--cookies", help="explicit JSON cookie export; never read automatically")
    parser.add_argument("--config", help="legacy config.ini path")
    parser.add_argument("--email", help="legacy Facebook email")
    parser.add_argument("--password", help="legacy Facebook password")


def _configure_logging(config=None):
    logger = Logger("fb2cal").getLogger()
    level = config.get("LOGGING", "level", fallback="INFO") if config is not None else "INFO"
    try:
        logger.setLevel(getattr(logging, level.upper()))
    except AttributeError as exc:
        raise ConfigurationError(f"Invalid logging level: {level}") from exc
    logging.getLogger().setLevel(logger.level)
    return logger


def _create_client(args, legacy=False):
    config = Config(path=args.config, required=legacy or not args.cookies).getConfig()
    _configure_logging(config)
    cookie_path = args.cookies or config.get("AUTH", "cookies_file", fallback="")
    if cookie_path:
        return FacebookClient(session=FacebookSession.from_cookie_file(cookie_path)), config
    email = args.email or config.get("AUTH", "fb_email", fallback="")
    password = args.password or config.get("AUTH", "fb_pass", fallback="")
    if not email or not password:
        raise ConfigurationError("Provide --cookies, or legacy --email/--password/config credentials")
    browser = FacebookBrowser()
    browser.authenticate(email, password)
    return browser, config


def _export_contacts(contacts, output_format, output_path):
    if not contacts:
        raise GraphQLSchemaError("Facebook returned no birthday contacts")
    if output_format == "json":
        writer = JSONExporter(contacts)
        content = writer.export()
    elif output_format == "vcf":
        writer = VCardExporter(contacts)
        content = writer.export()
    else:
        writer = ICSWriter(contacts)
        writer.generate()
        content = "".join(line.rstrip("\n") for line in writer.get_birthday_calendar())
    if output_path:
        writer.write(output_path)
    else:
        print(content, end="")


def _print_recap(contacts):
    summary = summarize_contacts(contacts)
    print(
        "Recap estrazione:\n"
        f"  amici con compleanno visibile: {summary.contacts}\n"
        f"  compleanni con anno: {summary.with_year}\n"
        f"  compleanni senza anno: {summary.without_year}\n"
        "  totale amici del profilo: non disponibile nella birthday query",
        file=sys.stderr,
    )


def run_export(args):
    client, _ = _create_client(args)
    client.validate_session()
    contacts = extract_birthdays(client)
    _export_contacts(contacts, args.format, args.output)
    _print_recap(contacts)
    return 0


def run_doctor(args):
    client, _ = _create_client(args)
    validation = client.validate_session()
    response = client.query_graph_ql_birthday_comet_monthly(0)
    Transformer().transform_birthday_comet_monthly_to_birthdays(response)
    result = {"session": validation.status, "user_id": validation.user_id, "fb_dtsg": "present", "graphql": "ok", "schema": "ok"}
    if args.json:
        print(json.dumps(result))
    else:
        print("Session: authenticated\nfb_dtsg: present\nGraphQL query: ok\nBirthday schema: ok")
    return 0


def run_legacy_config():
    config = Config(required=True).getConfig()
    _configure_logging(config)
    browser = FacebookBrowser()
    browser.authenticate(config["AUTH"]["FB_EMAIL"], config["AUTH"]["FB_PASS"])
    contacts = extract_birthdays(browser)
    if not contacts:
        raise GraphQLSchemaError("Facebook returned no birthday contacts")
    writer = ICSWriter(contacts)
    writer.generate()
    if strtobool(config["FILESYSTEM"].get("SAVE_TO_FILE", "True")):
        writer.write(config["FILESYSTEM"].get("ICS_FILE_PATH", "./out/birthdays.ics"))
    _print_recap(contacts)
    return 0


def _exit_code(error):
    if isinstance(error, (ConfigurationError, CookieFileError)):
        return 2
    if isinstance(error, AuthenticationError):
        return 3
    if isinstance(error, TokenExtractionError):
        return 4
    if isinstance(error, GraphQLQueryError):
        return 5
    if isinstance(error, GraphQLSchemaError):
        return 6
    return 1


def main(argv=None):
    argv = list(sys.argv[1:] if argv is None else argv)
    try:
        if not argv:
            return run_legacy_config()
        args = build_parser().parse_args(argv)
        if args.command == "export":
            return run_export(args)
        if args.command == "doctor":
            return run_doctor(args)
        build_parser().print_help()
        return 2
    except FacebookError as exc:
        print(f"fb2cal: {exc}", file=sys.stderr)
        return _exit_code(exc)
    except (KeyError, ValueError) as exc:
        print(f"fb2cal: invalid configuration: {exc}", file=sys.stderr)
        return 2
    finally:
        logging.shutdown()


if __name__ == "__main__":
    raise SystemExit(main())
