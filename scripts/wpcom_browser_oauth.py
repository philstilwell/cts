#!/usr/bin/env python3
"""Authorize WordPress.com in the browser and store a local OAuth token."""

from __future__ import annotations

import argparse
import getpass
from http.server import BaseHTTPRequestHandler, HTTPServer
import os
import secrets
import sys
from pathlib import Path
from typing import Any
from urllib.parse import parse_qs, urlencode, urlparse

from wpcom_get_token import (
    DEFAULT_SITE,
    DEFAULT_TOKEN_FILE,
    TOKEN_URL,
    find_site,
    mask_token,
    post_form,
    write_token_file,
)


AUTH_URL = "https://public-api.wordpress.com/oauth2/authorize"
DEFAULT_REDIRECT_URI = "http://localhost:8765/callback"
DEFAULT_SCOPES = "sites posts media taxonomy"


class CallbackHandler(BaseHTTPRequestHandler):
    server: "CallbackServer"

    def do_GET(self) -> None:  # noqa: N802 - stdlib callback name
        parsed = urlparse(self.path)
        if parsed.path != self.server.callback_path:
            self.send_response(404)
            self.end_headers()
            return

        params = parse_qs(parsed.query)
        self.server.query = params
        body = (
            "<!doctype html><title>WordPress.com Authorized</title>"
            "<p>Authorization received. You can return to Codex.</p>"
        ).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "text/html; charset=utf-8")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, format: str, *args: Any) -> None:
        return


class CallbackServer(HTTPServer):
    def __init__(self, server_address: tuple[str, int], callback_path: str) -> None:
        super().__init__(server_address, CallbackHandler)
        self.callback_path = callback_path
        self.query: dict[str, list[str]] | None = None


def prompt(name: str, label: str, *, secret: bool = False, default: str | None = None) -> str:
    value = os.environ.get(name)
    if value:
        return value
    if default is not None:
        typed = input(f"{label} [{default}]: ").strip()
        return typed or default
    if secret:
        value = getpass.getpass(f"{label}: ").strip()
    else:
        value = input(f"{label}: ").strip()
    if not value:
        raise SystemExit(f"Missing required value: {name}")
    return value


def first(params: dict[str, list[str]], key: str) -> str:
    values = params.get(key, [])
    return values[0] if values else ""


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--token-file", default=DEFAULT_TOKEN_FILE, help=f"default: {DEFAULT_TOKEN_FILE}")
    parser.add_argument("--site", default=os.environ.get("WPCOM_SITE", DEFAULT_SITE), help=f"default: {DEFAULT_SITE}")
    parser.add_argument("--redirect-uri", default=DEFAULT_REDIRECT_URI, help=f"default: {DEFAULT_REDIRECT_URI}")
    parser.add_argument("--scope", default=DEFAULT_SCOPES, help=f"default: {DEFAULT_SCOPES!r}")
    args = parser.parse_args()

    redirect = urlparse(args.redirect_uri)
    if redirect.hostname not in {"localhost", "127.0.0.1"} or not redirect.port or not redirect.path:
        raise SystemExit("--redirect-uri must be a localhost URL with an explicit port and path")

    client_id = prompt("WPCOM_CLIENT_ID", "WordPress.com OAuth client ID")
    client_secret = prompt("WPCOM_CLIENT_SECRET", "WordPress.com OAuth client secret", secret=True)
    state = secrets.token_urlsafe(24)
    authorize_url = f"{AUTH_URL}?{urlencode({
        'client_id': client_id,
        'redirect_uri': args.redirect_uri,
        'response_type': 'code',
        'blog': args.site,
        'scope': args.scope,
        'state': state,
    })}"

    server = CallbackServer((redirect.hostname, redirect.port), redirect.path)
    print("Open this authorization URL in the logged-in browser:")
    print(authorize_url)
    print(f"Waiting for WordPress.com to redirect to {args.redirect_uri} ...")
    server.handle_request()
    params = server.query or {}

    returned_state = first(params, "state")
    if not returned_state or returned_state != state:
        raise SystemExit("OAuth state did not match; refusing to exchange the code.")
    error = first(params, "error")
    if error:
        detail = first(params, "error_description")
        raise SystemExit(f"WordPress.com authorization failed: {error} {detail}".strip())
    code = first(params, "code")
    if not code:
        raise SystemExit(f"WordPress.com did not return an authorization code: {params}")

    token_data = post_form(
        TOKEN_URL,
        {
            "client_id": client_id,
            "client_secret": client_secret,
            "code": code,
            "grant_type": "authorization_code",
            "redirect_uri": args.redirect_uri,
        },
    )
    access_token = str(token_data.get("access_token", ""))
    token_type = str(token_data.get("token_type", "bearer"))
    if not access_token:
        raise SystemExit(f"Token exchange succeeded but no access_token was returned: {token_data}")

    site: dict[str, Any] = {}
    site_id = str(token_data.get("blog_id", ""))
    site_url = str(token_data.get("blog_url", args.site))
    if not site_id:
        site = find_site(access_token, args.site)
        site_id = str(site.get("ID", ""))
        site_url = str(site.get("URL", site_url))
    if not site_id:
        raise SystemExit(f"Could not identify numeric site ID from token response: {token_data}")

    token_file = Path(args.token_file)
    write_token_file(
        token_file,
        {
            "WPCOM_ACCESS_TOKEN": access_token,
            "WPCOM_TOKEN_TYPE": token_type,
            "WPCOM_SITE_ID": site_id,
            "WPCOM_SITE_URL": site_url,
            "WPCOM_SITE": args.site,
            "WPCOM_API_BASE": "https://public-api.wordpress.com",
        },
    )

    capabilities = site.get("capabilities", {})
    can_publish = capabilities.get("publish_posts") if isinstance(capabilities, dict) else None
    can_edit = capabilities.get("edit_posts") if isinstance(capabilities, dict) else None
    print(f"Wrote token file: {token_file}")
    print(f"Token: {mask_token(access_token)}")
    print(f"Site: {site_url} (ID {site_id})")
    if capabilities:
        print(f"Capabilities: edit_posts={can_edit}, publish_posts={can_publish}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
