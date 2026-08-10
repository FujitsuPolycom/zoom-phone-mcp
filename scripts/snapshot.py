import httpx, json, os, sys
from datetime import datetime, timedelta

client = httpx.Client(timeout=60)
base = "http://localhost:8767/mcp"
headers = {"Content-Type": "application/json", "Accept": "application/json, text/event-stream"}

resp = client.post(base, headers=headers, json={
    "jsonrpc": "2.0", "method": "initialize",
    "params": {"protocolVersion": "2024-11-05", "capabilities": {}, "clientInfo": {"name": "snapshot", "version": "1.0"}},
    "id": 1
})
sid = resp.headers.get("mcp-session-id", "")
headers["MCP-Session-Id"] = sid
client.post(base, headers=headers, json={"jsonrpc": "2.0", "method": "notifications/initialized"})

def call_tool(name, args={}):
    try:
        resp = client.post(base, headers=headers, json={
            "jsonrpc": "2.0", "method": "tools/call",
            "params": {"name": name, "arguments": args}, "id": 1
        }, timeout=60)
        for line in resp.text.split("\n"):
            if line.startswith("data: "):
                data = json.loads(line[6:])
                if "result" in data:
                    for c in data["result"].get("content", []):
                        text = c.get("text", "")
                        try:
                            obj = json.loads(text)
                            if obj.get("error"):
                                return {"status": "error", "message": obj.get("message", "")[:500]}
                            return {"status": "ok", "data": obj}
                        except:
                            if "coroutine" in text:
                                return {"status": "bug", "message": "coroutine not awaited"}
                            return {"status": "ok", "data": text[:500]}
                elif "error" in data:
                    return {"status": "rpc_error", "message": str(data["error"])[:500]}
        return {"status": "no_response"}
    except Exception as e:
        return {"status": "exception", "message": str(e)[:500]}

snapshot = {
    "timestamp": datetime.utcnow().isoformat() + "Z",
    "tool_results": {},
    "errors": [],
}

# Date range for report tools (last 30 days)
today = datetime.utcnow().strftime("%Y-%m-%d")
month_ago = (datetime.utcnow() - timedelta(days=30)).strftime("%Y-%m-%d")

# ── PHASE 1: List endpoints (no required args) ──
print("PHASE 1: List endpoints")
print("-" * 50)

list_tools = [
    "list_auto_receptionists",
    "list_call_queues",
    "list_phone_users",
    "list_phone_numbers",
    "list_devices",
    "list_sites",
    "list_common_areas",
    "list_routing_rules",
    "list_shared_line_groups",
    "list_calling_plans",
    "get_account_voicemails",
    "get_account_call_history",
    "list_call_recordings",
    "list_sms_sessions",
]

report_tools_with_dates = [
    ("get_call_charges", {"from_date": month_ago, "to_date": today}),
    ("get_fax_charges", {"from_date": month_ago, "to_date": today}),
    ("get_sms_charges", {"from_date": month_ago, "to_date": today}),
    ("get_operation_logs", {"from_date": month_ago, "to_date": today}),
    ("get_call_queue_analytics", {"from_date": month_ago, "to_date": today}),
]

collected = {}  # category -> list of {id, name, ...}

for tool_name in list_tools:
    result = call_tool(tool_name, {"page_size": 300})
    icon = "✅" if result["status"] == "ok" else "❌"
    data = result.get("data", {})
    
    # Extract items and IDs
    for key in ["auto_receptionists", "call_queues", "users", "phone_numbers", 
                 "devices", "sites", "common_areas", "routing_rules", 
                 "shared_line_groups", "calling_plans", "voicemails", "call_logs",
                 "recordings", "sms_sessions"]:
        if isinstance(data, dict) and key in data:
            items = data[key]
            if isinstance(items, list):
                collected[tool_name] = items
                count = len(items)
                # Get first ID for phase 2
                print(f"  {icon} {tool_name}: {count} items")
            break
    else:
        if isinstance(data, dict):
            total = data.get("total_records", "?")
            print(f"  {icon} {tool_name}: {total} records")
        else:
            print(f"  {icon} {tool_name}")
    
    if result["status"] != "ok":
        snapshot["errors"].append({"tool": tool_name, "error": result.get("message","")})
    snapshot["tool_results"][tool_name] = result.get("data", {})

for tool_name, args in report_tools_with_dates:
    result = call_tool(tool_name, args)
    icon = "✅" if result["status"] == "ok" else "❌"
    data = result.get("data", {})
    total = data.get("total_records", "?") if isinstance(data, dict) else "?"
    print(f"  {icon} {tool_name}: {total} records")
    if result["status"] != "ok":
        snapshot["errors"].append({"tool": tool_name, "error": result.get("message","")})
    snapshot["tool_results"][tool_name] = result.get("data", {})

# ── PHASE 2: Detail calls for each item ──
print("\nPHASE 2: Detail endpoints (per-item)")
print("-" * 50)

# Map list tool -> detail tools and their param name
detail_mapping = {
    "list_auto_receptionists": [
        ("get_auto_receptionist", "auto_receptionist_id", "id"),
        ("get_auto_receptionist_ivr", "auto_receptionist_id", "id"),
        ("get_ar_call_handling", "auto_receptionist_id", "id"),
        ("get_ar_policies", "auto_receptionist_id", "id"),
        ("get_ar_settings", "auto_receptionist_id", "id"),
    ],
    "list_call_queues": [
        ("get_call_queue", "call_queue_id", "id"),
        ("get_queue_call_handling", "call_queue_id", "id"),
        ("get_queue_settings", "call_queue_id", "id"),
        ("get_queue_policies", "call_queue_id", "id"),
        ("get_queue_recordings", "call_queue_id", "id"),
        ("list_queue_members", "call_queue_id", "id"),
        ("list_queue_custom_groups", "call_queue_id", "id"),
    ],
    "list_phone_users": [
        ("get_phone_user", "user_id", "id"),
        ("get_user_call_handling", "user_id", "id"),
        ("get_user_settings", "user_id", "id"),
    ],
    "list_phone_numbers": [
        ("get_phone_number", "phone_number_id", "id"),
    ],
    "list_devices": [
        ("get_device", "device_id", "id"),
    ],
    "list_sites": [
        ("get_site", "site_id", "id"),
    ],
    "list_common_areas": [
        ("get_common_area", "common_area_id", "id"),
        ("get_common_area_call_handling", "common_area_id", "id"),
    ],
    "list_routing_rules": [
        ("get_routing_rule", "routing_rule_id", "id"),
    ],
    "list_shared_line_groups": [
        ("get_shared_line_group", "shared_line_group_id", "id"),
    ],
}

total_detail_calls = 0
total_ok = 0
total_err = 0

for list_tool, detail_tools in detail_mapping.items():
    items = collected.get(list_tool, [])
    if not items:
        print(f"  ⏭️  {list_tool}: no items to detail")
        continue
    
    tool_short = list_tool.replace("list_", "").replace("_", " ")
    print(f"\n  📋 {list_tool} ({len(items)} items):")
    
    for dt_name, param_name, id_key in detail_tools:
        ok_count = 0
        err_count = 0
        for item in items:
            item_id = item.get(id_key) if isinstance(item, dict) else None
            if not item_id:
                continue
            result = call_tool(dt_name, {param_name: item_id})
            total_detail_calls += 1
            if result["status"] == "ok":
                ok_count += 1
                total_ok += 1
                # Store in snapshot
                key = f"{dt_name}:{item_id}"
                snapshot["tool_results"][key] = result.get("data", {})
            else:
                err_count += 1
                total_err += 1
                snapshot["errors"].append({"tool": dt_name, "id": item_id, "error": result.get("message","")[:200]})
        
        icon = "✅" if err_count == 0 else "⚠️"
        print(f"     {icon} {dt_name}: {ok_count} ok, {err_count} err")

# ── PHASE 3: User policies (requires policy_type) ──
print("\nPHASE 3: User policies (requires policy_type)")
print("-" * 50)

# Get user policies for first few users
users = collected.get("list_phone_users", [])
policy_types = ["outbound", "international", "sms", "voicemail", "recording", 
                "call_forwarding", "delegation", "auto_call_recording"]

for user in users[:5]:  # First 5 users
    user_id = user.get("id")
    user_name = user.get("name", user.get("email", user_id))
    print(f"\n  👤 {user_name} ({user_id}):")
    for pt in policy_types:
        result = call_tool("get_user_policies", {"user_id": user_id, "policy_type": pt})
        icon = "✅" if result["status"] == "ok" else "❌"
        print(f"     {icon} policy={pt}: {result['status']}")
        if result["status"] == "ok":
            snapshot["tool_results"][f"get_user_policies:{user_id}:{pt}"] = result.get("data", {})
        else:
            snapshot["errors"].append({"tool": "get_user_policies", "id": user_id, "policy_type": pt, "error": result.get("message","")[:200]})

# ── Summary ──
print("\n" + "=" * 60)
print("SNAPSHOT SUMMARY")
print("=" * 60)
print(f"  Timestamp: {snapshot['timestamp']}")
print(f"  List calls: {len(list_tools) + len(report_tools_with_dates)}")
print(f"  Detail calls: {total_detail_calls}")
print(f"  Total OK: {total_ok + len(list_tools) + len(report_tools_with_dates)}")
print(f"  Total errors: {total_err + len(snapshot['errors'])}")
print(f"  Unique data keys: {len(snapshot['tool_results'])}")

# Save snapshot
outpath = "/root/workspace/zoom-phone-mcp/snapshots"
os.makedirs(outpath, exist_ok=True)
fname = f"zoom_phone_snapshot_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.json"
fpath = os.path.join(outpath, fname)
with open(fpath, "w") as f:
    json.dump(snapshot, f, indent=2, default=str)
print(f"\n  Saved to: {fpath}")
print(f"  File size: {os.path.getsize(fpath) / 1024:.1f} KB")

# Print errors
if snapshot["errors"]:
    print(f"\n  ⚠️  {len(snapshot['errors'])} errors:")
    for e in snapshot["errors"][:10]:
        print(f"     - {e['tool']}: {e.get('error','')[:100]}")
    if len(snapshot["errors"]) > 10:
        print(f"     ... and {len(snapshot['errors']) - 10} more")

