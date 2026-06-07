from fastapi import FastAPI, HTTPException, Depends, Header
from pydantic import BaseModel
from typing import Optional
import re

app = FastAPI(title="MAC Address Validator API", version="1.0.0")
# === BT Builds Standard Middleware (auto-injected) ===
from fastapi.middleware.cors import CORSMiddleware as _BTCors
app.add_middleware(_BTCors, allow_origins=["*"], allow_methods=["*"],
    allow_headers=["*"], expose_headers=["X-RateLimit-Limit","X-RateLimit-Remaining","X-RateLimit-Reset"])

@app.middleware("http")
async def _bt_add_headers(request, call_next):
    response = await call_next(request)
    response.headers["X-Powered-By"] = "btbuilds"
    response.headers["Access-Control-Allow-Origin"] = "*"
    return response


# API key auth
API_KEY = "free-demo-key"

def verify_api_key(x_api_key: str = Header(None)):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# OUI vendor database (common vendors)
OUI_VENDORS = {
    "00:00:00": "Xerox",
    "00:00:01": "Xerox",
    "00:00:02": "Xerox",
    "00:00:09": "Xerox",
    "00:00:0C": "IEEE Registration Authority",
    "00:01:4C": "Cisco",
    "00:01:6C": "Cisco",
    "00:01:9B": "Cisco",
    "00:01:B4": "Cisco",
    "00:01:FC": "Cisco",
    "00:02:55": "Cisco",
    "00:02:6B": "Cisco",
    "00:02:B9": "Cisco",
    "00:02:F4": "Cisco",
    "00:03:47": "Cisco",
    "00:03:6B": "Cisco",
    "00:03:93": "Cisco",
    "00:03:E3": "Cisco",
    "00:04:20": "Cisco",
    "00:04:4F": "Cisco",
    "00:04:96": "Cisco",
    "00:04:CC": "Cisco",
    "00:04:DE": "Cisco",
    "00:04:FE": "Cisco",
    "00:05:00": "Cisco",
    "00:05:3C": "Cisco",
    "00:05:5E": "Cisco",
    "00:05:DC": "Cisco",
    "00:06:27": "Cisco",
    "00:06:41": "Cisco",
    "00:06:43": "Cisco",
    "00:06:5B": "Cisco",
    "00:06:66": "Cisco",
    "00:06:B0": "Cisco",
    "00:06:D6": "Cisco",
    "00:07:0E": "Cisco",
    "00:07:49": "Cisco",
    "00:07:4C": "Cisco",
    "00:07:54": "Cisco",
    "00:07:56": "Cisco",
    "00:07:A6": "Cisco",
    "00:07:B1": "Cisco",
    "00:07:B4": "Cisco",
    "00:07:D2": "Cisco",
    "00:07:E8": "Cisco",
    "00:07:F5": "Cisco",
    "00:08:A3": "Cisco",
    "00:08:C2": "Cisco",
    "00:09:6B": "Cisco",
    "00:0A:41": "Cisco",
    "00:0A:E5": "Cisco",
    "00:0B:45": "Cisco",
    "00:0B:5F": "Cisco",
    "00:0B:86": "Cisco",
    "00:0B:F6": "Cisco",
    "00:0C:29": "VMware",
    "00:0C:30": "VMware",
    "00:0C:41": "VMware",
    "00:0C:42": "VMware",
    "00:0C:85": "VMware",
    "00:0C:86": "VMware",
    "00:0C:E7": "Samsung Electronics",
    "00:0D:66": "Dell",
    "00:0D:93": "Dell",
    "00:0D:B9": "Dell",
    "00:0D:E9": "Dell",
    "00:0E:0C": "Dell",
    "00:0E:2E": "Dell",
    "00:0E:53": "Dell",
    "00:0E:A6": "Dell",
    "00:0E:C5": "Dell",
    "00:0F:20": "Dell",
    "00:0F:66": "Dell",
    "00:0F:86": "Dell",
    "00:0F:A3": "Dell",
    "00:11:25": "Dell",
    "00:11:43": "Dell",
    "00:11:80": "Dell",
    "00:11:E3": "Dell",
    "00:12:3F": "Dell",
    "00:12:DC": "Dell",
    "00:13:20": "Dell",
    "00:13:46": "Dell",
    "00:13:72": "Dell",
    "00:13:A9": "Dell",
    "00:13:C6": "Dell",
    "00:13:D6": "Dell",
    "00:14:22": "Dell",
    "00:14:5E": "Dell",
    "00:14:6C": "Dell",
    "00:15:5D": "Dell",
    "00:15:C5": "Dell",
    "00:16:3E": "VMware",
    "00:16:76": "Dell",
    "00:17:F2": "Dell",
    "00:18:F4": "Dell",
    "00:19:99": "Dell",
    "00:1A:4A": "Dell",
    "00:1A:A0": "Dell",
    "00:1B:21": "Dell",
    "00:1B:78": "Dell",
    "00:1C:42": "Dell",
    "00:1D:09": "Dell",
    "00:1D:60": "Dell",
    "00:1D:C1": "Dell",
    "00:1E:4F": "Dell",
    "00:1E:C1": "Dell",
    "00:1F:29": "Dell",
    "00:21:5A": "Dell",
    "00:21:5C": "Dell",
    "00:21:CC": "Dell",
    "00:22:19": "Dell",
    "00:22:33": "Apple",
    "00:22:41": "Apple",
    "00:22:68": "Apple",
    "00:23:12": "Apple",
    "00:23:32": "Apple",
    "00:23:5A": "Apple",
    "00:23:63": "Apple",
    "00:23:76": "Apple",
    "00:23:DF": "Apple",
    "00:24:1D": "Apple",
    "00:24:36": "Apple",
    "00:24:3F": "Apple",
    "00:24:B2": "Apple",
    "00:24:BB": "Apple",
    "00:24:EC": "Apple",
    "00:25:00": "Apple",
    "00:25:3C": "Apple",
    "00:25:4B": "Apple",
    "00:25:69": "Apple",
    "00:25:9C": "Apple",
    "00:25:A0": "Apple",
    "00:25:B3": "Apple",
    "00:25:BC": "Apple",
    "00:26:08": "Apple",
    "00:26:4A": "Apple",
    "00:26:90": "Apple",
    "00:26:B0": "Apple",
    "00:26:B7": "Apple",
    "00:26:BB": "Apple",
    "00:26:BE": "Apple",
    "00:26:C3": "Apple",
    "00:26:CA": "Apple",
    "00:26:D0": "Apple",
    "00:26:D9": "Apple",
    "00:26:E0": "Apple",
    "00:26:E7": "Apple",
    "00:26:ED": "Apple",
    "00:26:F0": "Apple",
    "00:26:F6": "Apple",
    "00:26:FF": "Apple",
    "00:27:18": "Apple",
    "00:27:19": "Apple",
    "00:27:32": "Apple",
    "00:27:40": "Apple",
    "00:27:4D": "Apple",
    "00:27:89": "Apple",
    "00:27:90": "Apple",
    "00:27:A5": "Apple",
    "00:27:AF": "Apple",
    "00:27:C7": "Apple",
    "00:27:EC": "Apple",
    "00:27:F4": "Apple",
    "00:27:F6": "Apple",
    "00:27:FA": "Apple",
    "00:27:FD": "Apple",
    "00:27:FE": "Apple",
    "00:27:FF": "Apple",
    "00:50:00": "IBM",
    "00:50:56": "VMware",
    "00:E0:4C": "IBM",
    "00:01:01": "3Com",
    "00:02:01": "3Com",
    "00:04:01": "3Com",
    "00:10:0D": "3Com",
    "00:10:20": "Intel",
    "00:10:5A": "Intel",
    "00:10:E0": "Intel",
    "00:11:11": "Intel",
    "00:11:6B": "Intel",
    "00:13:02": "Intel",
    "00:14:22": "Intel",
    "00:14:6C": "Intel",
    "00:15:17": "Intel",
    "00:17:88": "Intel",
    "00:19:D2": "Intel",
    "00:1B:21": "Intel",
    "00:1D:60": "Intel",
    "00:1E:67": "Intel",
    "00:22:69": "Intel",
    "00:24:54": "Intel",
    "00:27:1E": "Intel",
    "00:A0:B8": "Intel",
    "00:1C:C0": "Dell",
    "00:21:9B": "Dell",
    "00:26:22": "Dell",
    "00:26:73": "Dell",
    "B8:27:EB": "Raspberry Pi Foundation",
    "DC:A6:32": "Raspberry Pi Foundation",
    "D8:3A:DD": "Samsung Electronics",
    "D8:B0:53": "Samsung Electronics",
    "D4:61:9D": "Samsung Electronics",
    "CC:23:EA": "Samsung Electronics",
    "BC:1A:EC": "Samsung Electronics",
    "B4:EF:FA": "Samsung Electronics",
    "AC:D6:EC": "Samsung Electronics",
    "A0:6F:58": "Samsung Electronics",
    "94:65:9E": "Samsung Electronics",
    "88:36:50": "Samsung Electronics",
    "78:52:78": "Samsung Electronics",
    "70:F1:8C": "Samsung Electronics",
    "64:B3:E3": "Samsung Electronics",
    "5C:5F:D6": "Samsung Electronics",
    "54:19:2E": "Samsung Electronics",
    "48:45:20": "Samsung Electronics",
    "40:17:66": "Samsung Electronics",
    "38:30:F9": "Samsung Electronics",
    "30:39:24": "Samsung Electronics",
    "28:24:C2": "Samsung Electronics",
    "24:FD:25": "Samsung Electronics",
    "20:19:BD": "Samsung Electronics",
    "18:D6:39": "Samsung Electronics",
    "14:49:E0": "Samsung Electronics",
    "10:30:47": "Samsung Electronics",
    "08:21:A1": "Samsung Electronics",
    "04:87:E2": "Samsung Electronics",
    "0C:1D:AF": "Samsung Electronics",
    "F0:25:B0": "Samsung Electronics",
}

# MAC address regex patterns
MAC_PATTERNS = [
    re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$'),  # xx:xx:xx:xx:xx:xx or xx-xx-xx-xx-xx-xx
    re.compile(r'^([0-9A-Fa-f]{4}\.){2}([0-9A-Fa-f]{4})$'),  # xxxx.xxxx.xxxx
    re.compile(r'^[0-9A-Fa-f]{12}$'),  # 12 hex digits
]


def validate_mac(mac: str) -> bool:
    return any(pattern.match(mac) for pattern in MAC_PATTERNS)


def normalize_mac(mac: str) -> str:
    cleaned = re.sub(r'[^0-9A-Fa-f]', '', mac).upper()
    return ':'.join(cleaned[i:i+2] for i in range(0, 12, 2))


def get_oui(mac: str) -> str:
    normalized = normalize_mac(mac)
    oui = normalized[:8]
    # Convert xx:xx:xx to xx:xx:xx format (uppercase)
    oui_formatted = oui.upper()
    return OUI_VENDORS.get(oui_formatted, "Unknown")


class MACValidateRequest(BaseModel):
    mac_address: str


class MACValidateResponse(BaseModel):
    valid: bool
    normalized: Optional[str] = None
    oui: Optional[str] = None
    vendor: Optional[str] = None
    format_detected: Optional[str] = None


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/validate")
def validate_mac_address(request: MACValidateRequest, api_key: str = Depends(verify_api_key)):
    mac = request.mac_address.strip()
    
    if not mac:
        raise HTTPException(status_code=400, detail="MAC address is required")
    
    is_valid = validate_mac(mac)
    
    if not is_valid:
        return MACValidateResponse(valid=False)
    
    normalized = normalize_mac(mac)
    oui = normalized[:8].upper()
    
    # Detect format
    if re.match(r'^[0-9A-Fa-f]{12}$', mac):
        format_detected = "12-digit hex"
    elif re.match(r'^([0-9A-Fa-f]{4}\.){2}[0-9A-Fa-f]{4}$', mac):
        format_detected = "dot notation"
    else:
        format_detected = "colon/dash notation"
    
    vendor = OUI_VENDORS.get(oui, "Unknown")
    
    return MACValidateResponse(
        valid=True,
        normalized=normalized,
        oui=oui,
        vendor=vendor,
        format_detected=format_detected
    )

try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    pass
