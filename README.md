# MAC Address Validator API

Validate MAC addresses and extract vendor information from OUI.

## Endpoints

### GET /health
Health check endpoint. No API key required.

### POST /validate
Validate a MAC address, normalize it, and identify the vendor.

**Request Body:**
```json
{
  "mac_address": "00:1A:2B:3C:4D:5E"
}
```

**Response:**
```json
{
  "valid": true,
  "normalized": "00:1A:2B:3C:4D:5E",
  "oui": "00:1A:2B",
  "vendor": "Dell",
  "format_detected": "colon/dash notation"
}
```

## Usage

```bash
curl -X POST https://mac-validator.vercel.app/validate \
  -H "Content-Type: application/json" \
  -H "X-API-Key: free-demo-key" \
  -d '{"mac_address": "B8-27-EB-12-34-56"}'
```

## Supported Formats
- Colon notation: `00:1A:2B:3C:4D:5E`
- Dash notation: `00-1A-2B-3C-4D-5E`
- Dot notation: `001A.2B3C.4D5E`
- 12-digit hex: `001A2B3C4D5E`

## Features
- Validates MAC address format
- Normalizes to standard colon notation
- Extracts OUI (first 3 octets)
- Identifies vendor from built-in database
- Detects input format