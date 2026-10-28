# FIDE ratings

A small [Pyronaut](https://pyronaut.io/docs/) (Python on GraalPy, running in Micronaut) application that stores the monthly [FIDE rating lists](https://ratings.fide.com/download_lists.phtml) in SQLite and serves them:

- a home page with a FIDE ID search form, the number of players in the latest list, the top 10 by standard rating and a list of federations
- a federation page with that federation's top 10
- a player profile page with the latest standard, rapid and blitz ratings and a chart of the rating history (drawn with [pygal](https://www.pygal.org/))
- a JSON API to read the latest rating of a player and to import rating lists, secured with an API key

## Requirements

- The [Pyronaut CLI](https://pyronaut.io/docs/) (`pyronaut`)
- A GraalVM JDK (JVM packages need one)

## Run it

```bash
pyronaut install   # creates .venv (GraalPy) and installs pygal
pyronaut dev       # http://localhost:8080
```

`pyronaut dev` uses `config/application-dev.toml`, which points at the sample database in `data/` with a relative path, so it must be started from the project root. Open <http://localhost:8080/> and search for a FIDE ID that is in the sample, for example `535004274`.

`requests.http` has demo requests for PyCharm's HTTP client. Set `API_KEYS_IMPORTER_KEY` in its environment to the key the app uses to run the ones that save ratings. In dev that is the placeholder `xxx.yyy.zzz` from `application-dev.toml`; the same variable also sets the key on the server side (see Configuration), so exporting it before `pyronaut dev` keeps both in step.

### Sample database

`data/fide-ratings-sample.db` is committed so a fresh clone has something to show: a few hundred players across several months, with the Liquibase changesets already applied. Treat it as read-only sample data:

- SQLite runs in WAL mode, so the app creates `*.db-wal` and `*.db-shm` next to it. They are git-ignored.
- If the `.db` file shows up as modified after a dev session, restore it with `git checkout -- data/fide-ratings-sample.db` instead of committing it.
- Regenerate it deliberately when the schema changes, for example by importing a few players into a fresh database.

## Pages and API

| Method and path | What it does |
|---|---|
| `GET /` | Home page: search form, player count, top 10, federations |
| `GET /fide/ratings?fide_id=…` | Redirects (303) to the profile page; the home page form submits here |
| `GET /fide/ratings/{fide_id}` | Player profile with the rating chart (404 for an unknown player) |
| `GET /fide/ratings/federation/{fed}` | Top 10 players of a federation (404 if it has none) |
| `GET /api/v1/fide/ratings/{fide_id}/latest` | Latest rating of a player as JSON (404 if unknown) |
| `POST /api/v1/fide/ratings` | Saves a list of rating entries; needs the `X-API-KEY` header; skips entries already stored |
| `GET /swagger-ui/index.html` | Swagger UI; the spec is at `/swagger/fide-ratings-1.0.yml` |

The HTML pages are not part of the OpenAPI documentation.

## Importing rating lists

Download the lists from <https://ratings.fide.com/download_lists.phtml>, unzip them, and lay out the TXT files as `<folder>/<year>/<month>/<file>`:

```
fide/2026/10/standard_rating_list.txt
fide/2026/10/rapid_rating_list.txt
fide/2026/10/blitz_rating_list.txt
```

Then, with the app running:

```bash
API_KEYS_IMPORTER_KEY=<key> python3 scripts/import_ratings.py fide
```

The script reads only `.txt` files (the XML holds the same data), merges the standard, rapid and blitz files of each month, and sends the players in parallel batches with progress. Re-running is safe: entries already imported are skipped. `--from YYYY-MM` resumes after a failure, `--dry-run` reads without sending, and `--help` lists the other options.

## Configuration

Settings live in `config/application*.toml`. The values that differ per environment can be set with environment variables:

| Variable | Purpose |
|---|---|
| `DATASOURCES_DEFAULT_URL` | JDBC URL of the SQLite database, for example `jdbc:sqlite:/data/fide-ratings.db?journal_mode=WAL&busy_timeout=5000` |
| `API_KEYS_IMPORTER_NAME` | Name of the API key owner (`importer`) |
| `API_KEYS_IMPORTER_KEY` | The secret clients send in `X-API-KEY` |
| `MICRONAUT_SERVER_PORT` | HTTP port (default 8080) |

Schema changes go in new Liquibase changesets under `config/db/changelog/`; never edit one that has already been applied to a database, because Liquibase checks its checksum.

## Tests

```bash
pyronaut test
```

The tests use an in-memory SQLite database (`config/application-test.toml`) and the API key `test-key`. They cover the repository methods directly and the pages and API end to end.

## Code layout

`src/pyronaut_fide_ratings/` holds classless route modules, one per area:

- `player.py` – the `Player` entity and `PlayerRepository`
- `rating_controller.py` – the rating API, the profile page and the search redirect
- `home_controller.py`, `federation_controller.py` – the HTML pages
- `rating_chart.py`, `ranking.py`, `federation.py` – view models, the pygal chart, and federation names and flags
- `api_key.py` – API key authentication; `api_documentation.py` – the OpenAPI definition

Templates are in `config/views/` (Jinja, with `layout.jinja` as the shared page) and the style sheet is `config/public/styles.css`.

`PlayerRepository` has no SQL: Micronaut Data derives each query from the method name. Pyronaut does not translate Python-style names, so the names are camelCase keywords with the entity's snake_case property names, for example `findFirstByFide_idOrderByRating_yearDescAndRating_monthDesc`. Multi-column ordering is joined with `And`.

## Packaging

See the [Pyronaut packaging documentation](https://pyronaut.io/docs/#packaging).

## Micronaut documentation

- [Pyronaut documentation](https://pyronaut.io/docs/)
- [Micronaut user guide](https://docs.micronaut.io/latest/guide/index.html)
- [Micronaut Data](https://micronaut-projects.github.io/micronaut-data/latest/guide/)
- [Micronaut Security](https://micronaut-projects.github.io/micronaut-security/latest/guide/)
- [Micronaut Views](https://micronaut-projects.github.io/micronaut-views/latest/guide/)
