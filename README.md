# Seq Logs

Seq Logs is an Agent Zero plugin that lets agents fetch and inspect events from a [Seq](https://datalust.co/seq) centralized logging server using a Seq URL and API key.

## Features

- Fetch events from Seq's HTTP API
- Configure Seq URL and API key through Agent Zero settings
- Use Seq filter expressions to find logs by property, level, message text, or application
- Supports ISO-8601 `after` and `before` time bounds
- Returns structured JSON so Agent Zero can summarize, investigate, or report on logs

## Plugin files

```text
seq_logs/
├── plugin.yaml
├── default_config.yaml
├── README.md
├── LICENSE
├── helpers/
│   └── seq_client.py
├── tools/
│   └── fetch_seq_logs.py
└── webui/
    └── config.html
```

## Configuration

Open **Agent Zero Settings > External > Seq Logs** and set:

| Setting | Description |
|---|---|
| `seq_url` | Base URL for your Seq server, for example `https://seq.example.com` or `http://localhost:5341` |
| `api_key` | Seq API key with permission to query events |
| `lookback_minutes` | Optional default lookback window when no `after` time is provided |

The local `config.json` file is intentionally ignored by Git because it may contain private URLs and API keys.

## Tool

The plugin exposes the Agent Zero tool:

- `fetch_seq_logs`

### Arguments

| Argument | Required | Description |
|---|---:|---|
| `query` | No | Seq filter expression. Defaults to `*`. |
| `limit` | No | Maximum events to return. Capped at 500. Defaults to 50. |
| `after` | No | ISO-8601 lower time bound, e.g. `2026-06-30T00:00:00Z`. |
| `before` | No | ISO-8601 upper time bound. |
| `seq_url` | No | One-off Seq URL override. Otherwise reads plugin settings. |
| `api_key` | No | One-off API key override. Otherwise reads plugin settings. |

## Query examples

Find recent errors:

```json
{
  "query": "@Level = 'Error'",
  "limit": 25
}
```

Find events for an application:

```json
{
  "query": "[App Name] = 'MyService'",
  "limit": 50
}
```

Find events for a caller number property:

```json
{
  "query": "CallerNumber = '15551234567'",
  "limit": 50
}
```

Find events containing text:

```json
{
  "query": "Contains(@Message, 'Caller hung up')",
  "limit": 50
}
```

## Security and privacy

Seq logs often contain sensitive production data, including identifiers, phone numbers, user IDs, stack traces, hostnames, and internal URLs.

- Use a least-privilege Seq API key when possible.
- Do not commit `config.json` or any API key.
- Review logs before sharing model outputs externally.
- Be careful when querying or summarizing personally identifiable information.

## Development notes

This plugin uses Seq's `/api/events` endpoint and sends the user-provided expression through Seq's `filter` query parameter.

The tool class `FetchSeqLogs` subclasses Agent Zero's `helpers.tool.Tool`, and the module also keeps a simple `run()` function for smoke testing.

## License

MIT
