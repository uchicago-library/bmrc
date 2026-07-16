# BMRC Portal — Developer Notes

## What this is

A Django/Wagtail CMS for the Black Metropolis Research Consortium
(`bmrc.lib.uchicago.edu`), a University of Chicago library project.
The site has two distinct halves that are largely independent:

1. **Wagtail CMS** — editorial content (home page, news, standard pages,
   exhibits, curated topics). Standard Django/Wagtail patterns.

2. **Archival Portal** — a faceted search interface over EAD (Encoded
   Archival Description) finding aids stored in a MarkLogic XML database.
   Django does not store finding aid content in PostgreSQL at all.

---

## Local configuration

Real per-developer settings live in `bmrc/settings/local.py` (gitignored).
The important variables are:

- `MARKLOGIC_SERVER`, `MARKLOGIC_USERNAME`, `MARKLOGIC_PASSWORD` — connection
  to the MarkLogic REST API
- `PROXY_SERVER` — SOCKS5 proxy for off-campus MarkLogic access (SSH tunnel)
- `PAGE_LENGTH` — portal search results per page
- `SIDEBAR_VIEW_MORE_FACET_COUNT` / `SIDEBAR_VIEW_LESS_FACET_COUNT`
- `MAX_PAGE_LINKS` — pagination window size

`dev.py` and `production.py` both just import `local.py`.

---

## Django apps

| App | Purpose |
|---|---|
| `home` | `HomePage` — the site root (max 1) |
| `news` | `NewsIndexPage`, `NewsStoryPage` — news section |
| `portal` | Archival portal pages + all MarkLogic integration |
| `standard` | Generic `StandardPage` (no hierarchy restrictions) |
| `memb_collections` | Member collections search page |
| `search` | Site-wide Wagtail page search (`/search/`) |
| `site_settings` | Wagtail site settings: `FooterSettings`, `AlertBanner` |
| `streams` | Shared StreamField blocks used across all apps |

---

## Two separate search systems

- **`/search/`** — Wagtail database search over CMS page content. Nothing to
  do with MarkLogic.
- **`/portal/search/`** — Faceted full-text search over archival finding aids
  in MarkLogic. Completely separate from the above.

---

## MarkLogic integration

### Data model

MarkLogic is an XML document database. Each finding aid (an EAD XML file) is
stored as one document, identified by its filename (the EADID, e.g.
`BMRC.CHM.001.xml`). Documents are tagged with **collection URIs** — strings
like:

```
https://bmrc.lib.uchicago.edu/topics/Abolitionists
https://bmrc.lib.uchicago.edu/people/Ida+B.+Wells
https://bmrc.lib.uchicago.edu/archives/Chicago+History+Museum
https://bmrc.lib.uchicago.edu/decades/1920s
```

These collection URI tags are the mechanism behind faceted browsing and
filtering. A finding aid is tagged with one URI per controlled-vocabulary term
it contains across all six facet types: topics, people, places, organizations,
decades, archives.

### How Python talks to MarkLogic

All integration code is in `portal/__init__.py`. Two MarkLogic REST endpoints
are used:

- **`GET /v1/documents?uri=<uri>`** — fetch a single XML document
- **`POST /v1/eval`** — execute an XQuery script server-side; results come
  back as a multipart HTTP response decoded by `requests_toolbelt`; the payload
  is usually JSON

All calls use HTTP Basic auth. The optional `PROXY_SERVER` setting adds a
SOCKS5 proxy.

Note: `requests_cache` is imported but disabled — `setup_cache()` has an
unconditional `return` as its first line, so every MarkLogic call hits the
network.

### The four call paths

**Browse** (`/portal/browse/?b=<facet>`) → `get_collections.xqy`

Fetches all collection URIs matching a given prefix (e.g. all topics), along
with the EAD title of each finding aid in each collection. Python sorts and
paginates the result.

**Search** (`/portal/search/`) → `get_search.xqy`

The complex path (972-line XQuery). Takes a free-text query, active facet
filters, pagination, and sort order. Runs `cts:search()`, computes facet
counts via map intersection, and returns a JSON object with paginated results
plus six pairs of `active_*` / `more_*` facet arrays.

**View** (`/portal/view/?id=<eadid>`) → `GET /v1/documents` + XSLT

Fetches a single EAD XML document, then applies two XSLT transforms in Python
using `lxml`:
1. `portal/xslt/view.xsl` — EAD → HTML (1988 lines; handles all EAD 2002
   elements, turns controlled vocab terms into portal search links)
2. `portal/xslt/navigation.xsl` — generates a TOC sidebar from headings

After XSLT, `views.py` does regex post-processing on the HTML (fixes
self-closing divs, rewrites `<h1>` to `<hgroup>`, swaps Bootstrap class
names).

**Portal home page** → same `get_collections.xqy` as Browse

Each page load picks a random facet, fetches its collections, picks a random
collection for the "Discover More" widget. This is a live MarkLogic call on
every portal home page render.

### XSLT extension function

`view.xsl` calls `ucf:bmrc_search_url($namespace, $term)` — a Python function
registered as an lxml XSLT extension in `portal/views.py`:

```python
ns = etree.FunctionNamespace('https://lib.uchicago.edu/functions/')
ns['bmrc_search_url'] = bmrc_search_url
```

This is how every named entity in a displayed finding aid becomes a clickable
link that opens a filtered search.

### Dead XSLT files

- `portal/xslt/regularize.xsl` — normalizes EAD structure (see loading
  pipeline below); **not called** in the live `view` code path
- `portal/xslt/search.xsl` — stub; never wired into the live search path
- `portal/xslt/langcodes.xsl` — ISO 639 language code lookup; not called in
  current code

---

## Loading finding aids into MarkLogic

Finding aids are maintained as EAD XML files outside this repo, in a directory
with this structure:

```
findingaids/
  BMRC.CHM/          ← subdirectory named by archive prefix
    BMRC.CHM.001.xml
    BMRC.CHM.002.xml
  BMRC.ARC/
    BMRC.ARC.001.xml
```

The filename is the EADID and also the MarkLogic document URI.

### Step 1: Regularize (optional preprocessing)

```
python manage.py regularize-finding-aids <input_dir> <output_dir>
```

Applies two XSLT transforms to each EAD file:
1. `dtd2schema.xsl` — adds the EAD XML namespace (`urn:isbn:1-931666-22-9`),
   required for files created against the DTD
2. `regularize.xsl` — normalizes structure: adds missing `<head>` elements
   with standard English labels, converts `<c01>`–`<c12>` to generic `<c>`,
   supplies missing `@label` attributes, etc.

The `view` endpoint does **not** re-apply this transform at display time — it
shows whatever XML is in MarkLogic. So whether a finding aid displays correct
section headings depends on whether it was regularized before loading.

### Step 2: Load

```
python manage.py load-finding-aids <finding_aid_dir>
```

**Phase A — Build collection URIs in Python** by XPath-scanning every EAD
file on disk:

| Facet | XPath |
|---|---|
| topics | `//ead:genreform \| //ead:occupation \| //ead:subject` |
| people | `//ead:famname \| //ead:name \| //ead:persname` |
| places | `//ead:geogname` |
| organizations | `//ead:corpname` (excluding publisher/repository) |
| decades | parsed from `//ead:unitdate` (see below) |
| archives | filename prefix matched against `Archive.finding_aid_prefix` |

Each extracted term is URL-encoded and embedded in a URI like
`https://bmrc.lib.uchicago.edu/topics/Abolitionists`. The result is a dict
`{collection_uri: [list_of_eadids]}`.

Capitalization variants of the same term (e.g. "ida b. wells" vs "Ida B.
Wells") are collapsed by `merge_most_frequently_occurring_capitalizations()`,
which picks the capitalization appearing in the most finding aids.

Decade parsing uses a hand-written lexer that handles date ranges and lists
in free-text `<unitdate>` values. "1920–1945" expands to every year in that
range and maps each to a decade, so that finding aid gets tagged with
`1920s`, `1930s`, `1940s`, etc.

**Phase B — Upload** each EAD file to MarkLogic via `PUT /v1/documents`,
supplying all the collection URIs from Phase A that contain that file's EADID.
MarkLogic stores the XML and applies all the collection tags in one request.

### Delete all finding aids

```
python manage.py delete-all-finding-aids
```

Runs `delete_findingaids.xqy`, which deletes every document in the database.

---

## Authentication

The site uses University of Chicago Shibboleth SSO.
`django-shibboleth-remoteuser` (a fork) handles the middleware.
`AuthenticationMiddleware` appears twice in `MIDDLEWARE` — the second instance
is required by Shibboleth.

Shibboleth attribute mapping (SAML → Django user fields) is configured in
`bmrc/settings/base.py` under `SHIBBOLETH_ATTRIBUTE_MAP`.

---

## Bot protection

Cloudflare Turnstile (`django-turnstile-site-protect`, a fork) is applied
only to portal paths. `TURNSTILE_EXCLUDED_PATHS` in `base.py` excludes
everything except `/portal/`.

---

## Wagtail page hierarchy

```
HomePage (max 1)
├── PortalHomePage (max 1)
│   ├── CuratedTopicIndexPage (max 1)
│   │   └── CuratedTopicPage
│   └── ExhibitIndexPage (max 1)
│       └── ExhibitPage
├── StandardPage (no hierarchy restrictions; self-nesting allowed)
├── NewsIndexPage
│   └── NewsStoryPage (leaf)
└── MembCollectionIndexPage (max 1)
```

`PortalStandardPage` has no `parent_page_types` restriction so it can appear
anywhere in the tree. Several other `parent_page_types` / `subpage_types`
declarations in `portal/models.py` are commented out, making the hierarchy
more permissive than the above implies.

---

## Notable patterns

**Date-driven content rotation without cron.** Featured archive (monthly) and
featured curated topic (weekly) are computed at request time using modular
arithmetic on the current date — no scheduled jobs or database state.

**Accessibility enforcement in the model layer.** `streams/validators.py`
rejects generic alt text ("image", "photo", "logo", etc.) at save time for
all StreamField images. `NewsStoryPage.clean()` enforces the same on the lead
image. This is site-wide.

**`NoDbDjangoTestSuiteRunner`** skips database setup; `portal/tests.py` hits
the real MarkLogic dev server. This is set globally in `base.py` via
`TEST_RUNNER`.

**Sidebar pattern is duplicated across apps.** Each app defines its own
`SideBar` Orderable model with identical fields. This is intentional isolation,
not an oversight.

**Template organization.** All templates live centrally in
`bmrc/templates/`, with one subdirectory per app. The only exception is
`search/templates/` (inside the `search` app).
