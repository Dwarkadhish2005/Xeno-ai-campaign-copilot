"""
Full Project Test Suite - Xeno AI Campaign Copilot Backend
Tests all major API endpoints and DB interactions.
"""
import httpx
import json
import sys

BASE = "http://localhost:8000"
PASS = "\033[92m✔\033[0m"
FAIL = "\033[91m✘\033[0m"
INFO = "\033[94m→\033[0m"

results = []

def check(name, condition, detail=""):
    icon = PASS if condition else FAIL
    status = "PASS" if condition else "FAIL"
    print(f"  {icon} [{status}] {name}" + (f" — {detail}" if detail else ""))
    results.append((name, condition))

def section(title):
    print(f"\n{'='*55}")
    print(f"  {title}")
    print(f"{'='*55}")

def run_tests():
    client = httpx.Client(base_url=BASE, timeout=30)

    # ─── 1. Health Check ────────────────────────────────────────
    section("1. Health Check")
    try:
        r = client.get("/health")
        check("GET /health returns 200", r.status_code == 200, f"status={r.status_code}")
        data = r.json()
        check("Response has success=True", data.get("success") is True)
        check("Response has timestamp", "timestamp" in data.get("data", {}))
    except Exception as e:
        check("GET /health reachable", False, str(e))

    # ─── 2. Audience Endpoints ───────────────────────────────────
    section("2. Audience Endpoints")
    try:
        r = client.get("/audience/segments")
        check("GET /audience/segments returns 200", r.status_code == 200, f"status={r.status_code}")
        data = r.json()
        check("Response has success field", "success" in data)
    except Exception as e:
        check("GET /audience/segments reachable", False, str(e))

    try:
        r = client.get("/audience/customers?page=1&per_page=5")
        check("GET /audience/customers returns 200", r.status_code == 200, f"status={r.status_code}")
        data = r.json()
        check("Customers response has data key", "data" in data)
    except Exception as e:
        check("GET /audience/customers reachable", False, str(e))

    # ─── 3. Campaigns Endpoints ──────────────────────────────────
    section("3. Campaigns Endpoints")
    try:
        r = client.get("/campaigns")
        check("GET /campaigns returns 200", r.status_code == 200, f"status={r.status_code}")
        data = r.json()
        check("Campaigns list has total", "total" in data.get("data", {}))
        total = data.get("data", {}).get("total", 0)
        print(f"  {INFO} Total campaigns in DB: {total}")
    except Exception as e:
        check("GET /campaigns reachable", False, str(e))

    # ─── 4. AI Campaign Plan (Groq) ──────────────────────────────
    section("4. AI Campaign Plan (Groq API)")
    try:
        payload = {"business_goal": "Re-engage customers who haven't purchased in 90 days with a 15% discount"}
        r = client.post("/campaigns/plan", json=payload, timeout=60)
        check("POST /campaigns/plan returns 200", r.status_code == 200, f"status={r.status_code}")
        data = r.json()
        check("Plan response has success=True", data.get("success") is True)
        plan_data = data.get("data", {})
        check("Plan has campaign_name", bool(plan_data.get("campaign_name")))
        check("Plan has channel", bool(plan_data.get("channel")))
        check("Plan has filters", isinstance(plan_data.get("filters"), list))
        print(f"  {INFO} Campaign name: {plan_data.get('campaign_name', 'N/A')}")
        print(f"  {INFO} Channel: {plan_data.get('channel', 'N/A')}")
    except Exception as e:
        check("POST /campaigns/plan reachable", False, str(e))

    # ─── 5. Intelligence / Analytics ─────────────────────────────
    section("5. Intelligence Endpoints")
    try:
        r = client.get("/intelligence/insights")
        check("GET /intelligence/insights returns 200 or 404", r.status_code in (200, 404, 422), f"status={r.status_code}")
        if r.status_code == 200:
            data = r.json()
            check("Insights has success field", "success" in data)
    except Exception as e:
        check("GET /intelligence/insights reachable", False, str(e))

    # ─── 6. Analytics Endpoints ──────────────────────────────────
    section("6. Analytics Endpoints")
    try:
        r = client.get("/analytics/summary")
        check("GET /analytics/summary returns 200", r.status_code == 200, f"status={r.status_code}")
        data = r.json()
        check("Analytics summary has success", data.get("success") is True)
        summary = data.get("data", {})
        print(f"  {INFO} Total customers: {summary.get('total_customers', 'N/A')}")
        print(f"  {INFO} Total orders: {summary.get('total_orders', 'N/A')}")
        print(f"  {INFO} Total revenue: {summary.get('total_revenue', 'N/A')}")
    except Exception as e:
        check("GET /analytics/summary reachable", False, str(e))

    try:
        r = client.get("/analytics/campaigns")
        check("GET /analytics/campaigns returns 200", r.status_code == 200, f"status={r.status_code}")
    except Exception as e:
        check("GET /analytics/campaigns reachable", False, str(e))

    # ─── 7. OpenAPI Docs ─────────────────────────────────────────
    section("7. OpenAPI / Docs")
    try:
        r = client.get("/docs")
        check("GET /docs returns 200", r.status_code == 200)
        r2 = client.get("/openapi.json")
        check("GET /openapi.json returns 200", r2.status_code == 200)
        api = r2.json()
        paths = list(api.get("paths", {}).keys())
        print(f"  {INFO} Registered endpoints: {len(paths)}")
        for p in paths:
            print(f"      • {p}")
    except Exception as e:
        check("Docs reachable", False, str(e))

    # ─── Summary ─────────────────────────────────────────────────
    section("SUMMARY")
    passed = sum(1 for _, ok in results if ok)
    failed = sum(1 for _, ok in results if not ok)
    total = len(results)
    print(f"  {PASS} Passed: {passed}/{total}")
    if failed:
        print(f"  {FAIL} Failed: {failed}/{total}")
        print("\n  Failed tests:")
        for name, ok in results:
            if not ok:
                print(f"    {FAIL} {name}")
    print()
    return failed == 0

if __name__ == "__main__":
    print("\n🚀 Xeno AI Campaign Copilot — Full Project Test")
    print(f"   Target: {BASE}\n")
    success = run_tests()
    sys.exit(0 if success else 1)
