# MAC Address Validator API

Validate MAC addresses, convert formats, and identify vendors.

## Endpoints

### `GET /health`
Health check endpoint. No auth required.

```bash
curl https://mac-validator.vercel.app/health
```

### `POST /validate`
Validate a MAC address and get vendor info.

**Headers:** `X-API-Key: demo-key-change-in-production`

**Body:** Form data with `mac` field

```bash
curl -X POST https://mac-validator.vercel.app/validate \
  -H "X-API-Key: demo-key-change-in-production" \
  -d "mac=00:1A:2B:3C:4D:5E"
```

**Response:**
```json
{
  "valid": true,
  "original": "00:1A:2B:3C:4D:5E",
  "normalized": "00:1A:2B:3C:4D:5E",
  "vendor": "Unknown"
}
```

### `POST /validate/batch`
Validate multiple MAC addresses.

```bash
curl -X POST https://mac-validator.vercel.app/validate/batch \
  -H "X-API-Key: demo-key-change-in-production" \
  -H "Content-Type: application/json" \
  -d '{"macs": ["00:1A:2B:3C:4D:5E", "00:25:64:12:34:56"]}'
```

### `GET /format?mac=...&format_type=...`
Convert MAC address to different formats.

**Headers:** `X-API-Key: demo-key-change-in-production`

**Params:**
- `mac` - MAC address to convert
- `format_type` (optional) - Format to convert to

```bash
curl "https://mac-validator.vercel.app/format?mac=00-1A-2B-3C-4D-5E" \
  -H "X-API-Key: demo-key-change-in-production"
```

## Supported Formats

- `colon` (default): `00:1A:2B:3C:4D:5E`
- `dash`: `00-1A-2B-3C-4D-5E`
- `dot`: `001A.2B3C.4D5E`
- `none`: `001A2B3C4D5E`

## Supported MAC Formats

- `00:1A:2B:3C:4D:5E`
- `00-1A-2B-3C-4D-5E`
- `001A.2B3C.4D5E`
- `001A2B3C4D5E`

## Monetization

- List on RapidAPI: $15/month
- Target: Network administrators, IoT developers, security teams