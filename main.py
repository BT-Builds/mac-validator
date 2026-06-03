import re
from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel
import os

app = FastAPI(title="MAC Address Validator API", version="1.0.0")

API_KEY = os.getenv("API_KEY", "demo-key-change-in-production")

def verify_api_key(x_api_key: str = None):
    if not x_api_key or x_api_key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return x_api_key

# Common vendor OUIs
OUI_VENDORS = {
    "00:00:00": "Xerox",
    "00:01:42": "Cisco",
    "00:02:39": "Cisco",
    "00:0D:65": "Cisco",
    "00:0D:93": "Cisco",
    "00:0F:66": "Cisco",
    "00:12:00": "Cisco",
    "00:12:43": "Cisco",
    "00:13:1A": "Cisco",
    "00:13:60": "Cisco",
    "00:14:22": "Cisco",
    "00:16:47": "Cisco",
    "00:17:9A": "Cisco",
    "00:18:18": "Cisco",
    "00:18:71": "Cisco",
    "00:19:07": "Cisco",
    "00:1A:2A": "Cisco",
    "00:1B:53": "Cisco",
    "00:1C:57": "Cisco",
    "00:1D:A2": "Cisco",
    "00:1E:13": "Cisco",
    "00:1E:7A": "Cisco",
    "00:1F:6C": "Cisco",
    "00:21:1B": "Cisco",
    "00:21:A0": "Cisco",
    "00:22:BD": "Cisco",
    "00:22:C9": "Cisco",
    "00:23:04": "Cisco",
    "00:23:3A": "Cisco",
    "00:23:EB": "Cisco",
    "00:24:0D": "Cisco",
    "00:24:54": "Apple",
    "00:24:B2": "Apple",
    "00:25:00": "Apple",
    "00:25:4B": "Apple",
    "00:26:08": "Apple",
    "00:26:BB": "Apple",
    "00:3E": "Apple",
    "04:15": "Apple",
    "04:F1": "Apple",
    "08:60": "Apple",
    "0C:15": "Apple",
    "10:1B": "Apple",
    "14:18": "Apple",
    "18:34": "Apple",
    "18:64": "Apple",
    "1C:1A": "Apple",
    "28:3A": "Apple",
    "28:6A": "Apple",
    "28:6C": "Apple",
    "34:15": "Apple",
    "38:0B": "Apple",
    "3C:15": "Apple",
    "40:3C": "Apple",
    "44:D8": "Apple",
    "48:43": "Apple",
    "4C:86": "Apple",
    "50:ED": "Apple",
    "54:26": "Apple",
    "58:55": "Apple",
    "5C:96": "Apple",
    "60:33": "Apple",
    "60:F8": "Apple",
    "64:9A": "Apple",
    "68:09": "Apple",
    "68:A8": "Apple",
    "6C:16": "Apple",
    "70:11": "Apple",
    "74:F0": "Apple",
    "78:A7": "Apple",
    "7C:01": "Apple",
    "80:4E": "Apple",
    "84:11": "Apple",
    "88:53": "Apple",
    "88:A7": "Apple",
    "90:75": "Apple",
    "94:F1": "Apple",
    "98:03": "Apple",
    "9C:43": "Apple",
    "A0:99": "Apple",
    "A4:51": "Apple",
    "A8:20": "Apple",
    "A8:66": "Apple",
    "B8:17": "Apple",
    "B8:C6": "Apple",
    "BC:3B": "Apple",
    "C0:3B": "Apple",
    "C4:B3": "Apple",
    "C8:1F": "Apple",
    "CC:08": "Apple",
    "D0:3E": "Apple",
    "D4:9A": "Apple",
    "D8:00": "Apple",
    "D8:96": "Apple",
    "DC:53": "Apple",
    "E0:66": "Apple",
    "E4:8B": "Apple",
    "EC:3D": "Apple",
    "F0:B4": "Apple",
    "F4:1F": "Apple",
    "F8:06": "Apple",
    "FC:E8": "Apple",
    "00:50:B6": "Microsoft",
    "00:03:FF": "Microsoft",
    "00:04:20": "Microsoft",
    "00:0A:17": "Microsoft",
    "00:0D:3A": "Microsoft",
    "00:12:5A": "Microsoft",
    "00:18:22": "Microsoft",
    "00:19:47": "Microsoft",
    "00:1B:77": "Microsoft",
    "00:1C:42": "Microsoft",
    "00:1E:8C": "Microsoft",
    "00:22:6B": "Microsoft",
    "00:25:AE": "Microsoft",
    "00:2A:72": "Microsoft",
    "00:2D:41": "Microsoft",
    "00:34:FB": "Microsoft",
    "00:40:F3": "Microsoft",
    "00:50:F2": "Microsoft",
    "00:53:CC": "Microsoft",
    "00:A0:8F": "Microsoft",
    "00:B0:D0": "Microsoft",
    "00:D0:F5": "Microsoft",
    "00:15:5D": "Microsoft",
    "00:17:FA": "Microsoft",
    "00:1D:58": "Microsoft",
    "00:24:09": "Microsoft",
    "00:26:6C": "Microsoft",
    "40:23": "Samsung",
    "B4:60": "Samsung",
    "B8:81": "Samsung",
    "BC:7B": "Samsung",
    "C0:A9": "Samsung",
    "C4:57": "Samsung",
    "CC:B3": "Samsung",
    "D0:81": "Samsung",
    "D4:36": "Samsung",
    "D8:43": "Samsung",
    "DC:57": "Samsung",
    "E0:5A": "Samsung",
    "E4:33": "Samsung",
    "E8:56": "Samsung",
    "EC:F9": "Samsung",
    "F0:E6": "Samsung",
    "F4:8C": "Samsung",
    "F8:2A": "Samsung",
    "FC:A8": "Samsung",
    "00:09:0F": "Dell",
    "00:11:43": "Dell",
    "00:13:CE": "Dell",
    "00:14:22": "Dell",
    "00:1E:C9": "Dell",
    "00:21:70": "Dell",
    "00:25:64": "Dell",
    "00:80:F0": "Dell",
    "04:13:3E": "HP",
    "08:2E:5F": "HP",
    "10:60:77": "HP",
    "14:58:D0": "HP",
    "18:66:DA": "HP",
    "1C:C1:DE": "HP",
    "20:04:D9": "HP",
    "24:BE:05": "HP",
    "28:80:22": "HP",
    "2C:1B:9C": "HP",
    "30:65:EC": "HP",
    "34:E6:D7": "HP",
    "38:2C:4A": "HP",
    "3C:D9:23": "HP",
    "40:58:ED": "HP",
    "44:2E:34": "HP",
    "48:5D:54": "HP",
    "4C:5E:90": "HP",
    "50:30:E9": "HP",
    "54:6E:EA": "HP",
    "58:CA:58": "HP",
    "5C:3F:C6": "HP",
    "60:6D:23": "HP",
    "64:80:99": "HP",
    "68:B5:99": "HP",
    "6C:F0:29": "HP",
    "70:85:C2": "HP",
    "74:23:87": "HP",
    "78:76:87": "HP",
    "7C:D9:5C": "HP",
    "80:D4:E9": "HP",
    "84:2B:2B": "HP",
    "88:51:FB": "HP",
    "8C:06:52": "HP",
    "90:61:AE": "HP",
    "94:18:35": "HP",
    "98:BEC:3F": "HP",
    "9C:D3:6B": "HP",
    "A0:48:1C": "HP",
    "A4:CE:D0": "HP",
    "A8:2A:DE": "HP",
    "AC:9E:17": "HP",
    "B0:5C:C9": "HP",
    "B4:E8:2B": "HP",
    "B8:D9:44": "HP",
    "BC:30:5B": "HP",
    "C0:74:AD": "HP",
    "C4:37:8B": "HP",
    "C8:D7:19": "HP",
    "CC:79:66": "HP",
    "D0:69:57": "HP",
    "D4:03:9F": "HP",
    "D8:8B:47": "HP",
    "DC:85:F1": "HP",
    "E0:DB:55": "HP",
    "E4:CE:7E": "HP",
    "E8:9A:21": "HP",
    "EC:FB:39": "HP",
    "F0:2F:74": "HP",
    "F4:39:85": "HP",
    "F8:4F:3B": "HP",
    "00:90:FB": "Intel",
    "00:02:6B": "Intel",
    "00:04:20": "Intel",
    "00:07:E9": "Intel",
    "00:0C:6A": "Intel",
    "00:0D:65": "Intel",
    "00:0E:0C": "Intel",
    "00:11:24": "Intel",
    "00:13:02": "Intel",
    "00:16:EA": "Intel",
    "00:1B:21": "Intel",
    "00:1B:FC": "Intel",
    "00:1E:66": "Intel",
    "00:1F:16": "Intel",
    "00:21:55": "Intel",
    "00:22:30": "Intel",
    "00:24:D7": "Intel",
    "00:26:73": "Intel",
    "00:A0:C5": "Intel",
    "00:A0:C9": "Intel",
    "04:1E:67": "Intel",
    "04:D9:F5": "Intel",
    "0C:8B:7D": "Intel",
    "10:7B:E6": "Intel",
    "14:CC:20": "Intel",
    "18:26:B4": "Intel",
    "18:66:DA": "Intel",
    "1C:6F:65": "Intel",
    "20:66:C7": "Intel",
    "24:4B:FE": "Intel",
    "28:CC:00": "Intel",
    "28:F1:A3": "Intel",
    "2C:41:38": "Intel",
    "30:39:29": "Intel",
    "34:DE:6F": "Intel",
    "38:2C:4A": "Intel",
    "3C:07:54": "Intel",
    "3C:D9:23": "Intel",
    "40:7C:FD": "Intel",
    "44:03:CF": "Intel",
    "48:45:20": "Intel",
    "4C:71:3F": "Intel",
    "50:7B:9D": "Intel",
    "54:13:E9": "Intel",
    "58:6D:BB": "Intel",
    "5C:85:2A": "Intel",
    "60:36:DD": "Intel",
    "64:80:99": "Intel",
    "68:EB:87": "Intel",
    "6C:3B:D2": "Intel",
    "70:5A:0F": "Intel",
    "74:6D:2B": "Intel",
    "78:24:AF": "Intel",
    "7C:21:05": "Intel",
    "80:19:34": "Intel",
    "84:A1:58": "Intel",
    "88:A7:9A": "Intel",
    "8C:06:52": "Intel",
    "90:32:63": "Intel",
    "94:29:8B": "Intel",
    "98:5F:D3": "Intel",
    "9C:F4:8F": "Intel",
    "A0:D3:32": "Intel",
    "A4:04:5C": "Intel",
    "A8:20:C2": "Intel",
    "AC:2B:17": "Intel",
    "B0:51:93": "Intel",
    "B4:96:AC": "Intel",
    "B8:2A:EC": "Intel",
    "BC:6C:87": "Intel",
    "C0:3F:D6": "Intel",
    "C4:34:68": "Intel",
    "C8:9C:DC": "Intel",
    "CC:52:AF": "Intel",
    "D0:57:7B": "Intel",
    "D4:BE:D9": "Intel",
    "D8:30:98": "Intel",
    "DC:53:65": "Intel",
    "E0:94:EB": "Intel",
    "E4:A4:71": "Intel",
    "E8:4E:06": "Intel",
    "EC:59:FB": "Intel",
    "F0:13:2D": "Intel",
    "F4:6D:04": "Intel",
    "F8:75:A4": "Intel",
}

def normalize_mac(mac: str) -> str:
    clean = re.sub(r'[:-\.\s]', '', mac).upper()
    if len(clean) != 12:
        raise ValueError("Invalid MAC address length")
    return ':'.join(clean[i:i+2] for i in range(0, 12, 2))

def validate_mac_format(mac: str) -> bool:
    clean = re.sub(r'[:-\.\s]', '', mac).upper()
    return bool(re.match(r'^[0-9A-F]{12}$', clean))

def get_vendor(mac: str) -> str:
    normalized = normalize_mac(mac).upper()
    oui_key = ':'.join(normalized.split(':')[:3])
    vendor = OUI_VENDORS.get(oui_key)
    if not vendor:
        oui_key = ':'.join(normalized.split(':')[:2])
        vendor = OUI_VENDORS.get(oui_key)
    if not vendor:
        oui_key = normalized.split(':')[0]
        vendor = OUI_VENDORS.get(oui_key)
    return vendor or "Unknown"

@app.get("/health")
def health():
    return {"status": "ok"}

@app.post("/validate")
def validate_mac(mac: str, api_key: str = Depends(verify_api_key)):
    if not validate_mac_format(mac):
        raise HTTPException(status_code=400, detail="Invalid MAC address format")
    normalized = normalize_mac(mac)
    vendor = get_vendor(mac)
    return {"valid": True, "original": mac, "normalized": normalized, "vendor": vendor}

class MacBatch(BaseModel):
    macs: list[str]

@app.post("/validate/batch")
def validate_mac_batch(payload: MacBatch, api_key: str = Depends(verify_api_key)):
    results = []
    for mac in payload.macs:
        try:
            normalized = normalize_mac(mac) if validate_mac_format(mac) else None
            if normalized:
                results.append({
                    "original": mac,
                    "valid": True,
                    "normalized": normalized,
                    "vendor": get_vendor(mac)
                })
            else:
                results.append({"original": mac, "valid": False, "error": "Invalid format"})
        except Exception as e:
            results.append({"original": mac, "valid": False, "error": str(e)})
    return {"results": results}

@app.get("/format")
def format_mac(mac: str, format_type: str = "colon", api_key: str = Depends(verify_api_key)):
    if not validate_mac_format(mac):
        raise HTTPException(status_code=400, detail="Invalid MAC address format")
    normalized = normalize_mac(mac)
    clean = normalized.replace(':', '')
    formats = {
        "colon": normalized,
        "dash": '-'.join(clean[i:i+2] for i in range(0, 12, 2)),
        "dot": '.'.join(clean[i:i+4] for i in range(0, 12, 4)),
        "none": clean,
        "upper": clean,
        "lower": clean.lower()
    }
    return {"original": mac, "formats": formats}

try:
    from mangum import Mangum
    handler = Mangum(app, lifespan="off")
except ImportError:
    pass
