"""Persisted Facebook GraphQL birthday query definition and parsing."""

from __future__ import annotations

import json
from typing import Any

from .errors import GraphQLQueryError, GraphQLSchemaError, PersistedQueryError
from .utils import remove_anti_hijacking_protection

GRAPHQL_ENDPOINT = "https://www.facebook.com/api/graphql/"
BIRTHDAY_QUERY_NAME = "BirthdayCometMonthlyBirthdaysRefetchQuery"
BIRTHDAY_QUERY_DOC_ID = 5347559575302259


def build_birthday_payload(offset_month: int, fb_dtsg: str) -> dict[str, str | int]:
    if offset_month not in (0, 3, 6, 9):
        raise ValueError("offset_month must be one of 0, 3, 6, or 9")
    variables = {"offset_month": offset_month, "scale": 1.5}
    return {
        "fb_api_req_friendly_name": BIRTHDAY_QUERY_NAME,
        "variables": json.dumps(variables, separators=(",", ":")),
        "doc_id": BIRTHDAY_QUERY_DOC_ID,
        "fb_dtsg": fb_dtsg,
        "__a": "1",
    }


def parse_birthday_response(text: str) -> dict[str, Any]:
    try:
        response = json.loads(remove_anti_hijacking_protection(text))
    except (TypeError, json.JSONDecodeError) as exc:
        raise GraphQLQueryError("Facebook returned invalid GraphQL JSON") from exc

    if not isinstance(response, dict):
        raise GraphQLSchemaError("Facebook GraphQL response is not an object")
    if response.get("error") is not None or response.get("errors"):
        summary = response.get("errorSummary") or response.get("errorDescription") or "unknown GraphQL error"
        message = str(summary)
        if "doc" in message.lower() or "persist" in message.lower() or "query" in message.lower():
            raise PersistedQueryError(
                f"Facebook persisted query {BIRTHDAY_QUERY_NAME} (doc_id {BIRTHDAY_QUERY_DOC_ID}) "
                "may be obsolete; update the query definition."
            )
        raise GraphQLQueryError(f"Facebook birthday GraphQL request failed: {message}")

    data = response.get("data")
    if not isinstance(data, dict):
        raise GraphQLSchemaError("Facebook GraphQL response does not contain a data object")
    return response
