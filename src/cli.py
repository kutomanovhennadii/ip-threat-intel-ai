import sys
import httpx

API_URL = "http://127.0.0.1:8000/api/analyze-ip"


def format_bool(v):
    if v is True:
        return "Yes"
    if v is False:
        return "No"
    return "—"


def main():
    if len(sys.argv) != 2:
        print("Usage: python cli.py <ip-address>")
        sys.exit(1)

    ip = sys.argv[1]
    url = f"{API_URL}?ip={ip}"

    print(f"Querying: {url}\n")

    try:
        resp = httpx.get(url, timeout=10.0)
    except Exception as e:
        print(f"Request failed: {e}")
        sys.exit(1)

    if resp.status_code != 200:
        print(f"Error: HTTP {resp.status_code}")
        print(resp.text)
        sys.exit(1)

    data = resp.json()

    print("=== IP Threat Intelligence Report ===\n")

    print(f"IP Address:        {data.get('ip')}")
    print(f"Hostname:          {data.get('hostname') or '—'}")
    print(f"ISP:               {data.get('isp') or '—'}")
    print(f"Country:           {data.get('country') or '—'}\n")

    print(f"Abuse Score:       {data.get('abuse_score')}")
    print(f"Recent Reports:    {data.get('recent_reports')}")
    print(f"VPN/Proxy:         {format_bool(data.get('vpn_proxy'))}")
    print(f"Fraud Score:       {data.get('fraud_score')}")
    print(f"Risk Score (calc): {data.get('risk_score')}\n")

    print(f"AI Risk Level:     {data.get('risk_level')}\n")
    print("AI Analysis:")
    print(data.get("risk_analysis") or "—")
    print("\nRecommendations:")
    print(data.get("recommendations") or "—")
    print("\n======================================")


if __name__ == "__main__":
    main()
