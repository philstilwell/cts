# WordPress.com Automation Setup

This project uses the WordPress.com REST API for automated publishing to the Christian Thought Survey site.

## Weekly Survey Content Rule

When WordPress pages or posts describe a Weekly Survey, they should match the GitHub Pages language:

1. One CTS-administered topic: 12 related survey items from the CTS topic bank.
2. Three participant-vote-determined questions: 3 additional live survey items chosen based on the previous week's participant vote. These should be independent from the weekly CTS-administered topic.
3. A participant-nominated item ballot: 7 AI-polished ballot items selected from the previous week's participant nominations. If fewer than 7 suitable participant nominations are available, CTS adds AI-created seed items to complete the ballot. Ballot items should be clear, relevant, novel, independent from the weekly topic, and likely to generate meaningful disagreement or spread.
4. A text box to suggest survey items to be voted on next week and possibly featured in the following week's survey.
5. Last week's results summary and link: a brief summary and a link to the primary CTS website page containing the previous week's results and reports.

All live survey items should be credence-based slider items. The only non-slider inputs should be the participant-nominated item ballot and suggestion text boxes.

When describing the participant-nominated ballot, make clear that CTS reviews suggestions with AI assistance, polishes them for clarity, neutrality, credence-slider suitability, breadth, orthogonality to the weekly topic, novelty, tension potential, and pastoral or theological relevance, and presents 7 ballot items for active participants to rank. The top 3 ranked eligible items become live survey items in the following week's survey. The older 200-item CTS survey may be indexed as a reference pool for themes or seed ideas when useful, but current weekly items should be rewritten for clarity rather than copied mechanically.

## Authentication Model

WordPress.com requires OAuth2 bearer tokens for authenticated API requests. For a personal automation that publishes only to our own site, the practical setup is:

1. Create a WordPress.com developer application to obtain `client_id` and `client_secret`.
2. Authorize the application in the browser using the registered localhost redirect URI and site-scoped permissions.
3. Store only the resulting bearer token locally for automation.

The local token file is ignored by git at `.secrets/wordpress.env`.

## One-Time Browser Authorization

Run:

```bash
python3 scripts/wpcom_browser_oauth.py
```

The script will prompt for the WordPress.com OAuth client ID and client secret, print an authorization URL, wait for the local callback, then write:

```bash
.secrets/wordpress.env
```

## Password-Grant Token Exchange

WordPress.com also supports a password grant for development and testing. If two-step authentication is enabled on the WordPress.com account, create an application password first and use that instead of the account password.

Run:

```bash
python3 scripts/wpcom_get_token.py
```

The script will prompt for any missing values:

- WordPress.com OAuth client ID
- WordPress.com OAuth client secret
- WordPress.com username
- WordPress.com application password
- site domain, defaulting to `christianthoughtsurvey.wordpress.com`

It writes:

```bash
.secrets/wordpress.env
```

The file contains the bearer token, numeric WordPress.com site ID, and a few non-secret API settings. It does not store the WordPress.com application password or OAuth client secret.

## Verify Later

After setup, scripts can source the token file:

```bash
set -a
source .secrets/wordpress.env
set +a
```

Then authenticated API calls can use:

```bash
Authorization: Bearer $WPCOM_ACCESS_TOKEN
```

With the site-scoped token, use WordPress.com's v1.1 REST API endpoints:

```text
https://public-api.wordpress.com/rest/v1.1/sites/$WPCOM_SITE_ID/posts/
https://public-api.wordpress.com/rest/v1.1/sites/$WPCOM_SITE_ID/posts/new
https://public-api.wordpress.com/rest/v1.1/sites/$WPCOM_SITE_ID/media/new
```

To create pages instead of posts, send `type=page` to the `posts/new` endpoint.

The newer `wp/v2/sites/...` WordPress.com endpoints currently require the broader `global` OAuth scope. We are avoiding that unless the weekly publishing workflow turns out to need it.
