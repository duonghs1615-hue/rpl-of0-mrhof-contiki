from __future__ import annotations

import argparse
import csv
import ipaddress
import re
import statistics
from collections import defaultdict, deque
from pathlib import Path

ANSI_RE = re.compile(r"\x1b\[[0-9;]*[A-Za-z]")
TIME_NODE_RE = re.compile(
    r"^\s*(?P<minutes>\d+):(?P<seconds>\d{2})\.(?P<fraction>\d{1,6})\s+ID:\s*(?P<node>\d+)\b"
)
SEND_RE = re.compile(r"\bSending request\s+(?P<seq>\d+)\s+to\b", re.I)
RECV_RE = re.compile(
    r"\bReceived request\s+['\"]hello\s+(?P<seq>\d+)['\"]\s+from\s+(?P<ip>[0-9a-fA-F:.]+)",
    re.I,
)
FORWARD_RE = re.compile(
    r"\bext hdr: packet from\s+(?P<src>[0-9a-fA-F:.]+)\s+to\s+"
    r"(?P<dst>[0-9a-fA-F:.]+)\s+going up\b", re.I
)
PARENT_RE = re.compile(r"\bparent switch:\s*(?P<old>.*?)\s*->\s*(?P<new>\S.*)$", re.I)
OCP_RE = re.compile(r"\bDAG state:\s*joined,\s*MOP\s+\d+\s+OCP\s+(?P<ocp>\d+)\b", re.I)
SEED_RE = re.compile(r"(?:^|[_-])seed[_-]?(\d+)(?:$|[_-])", re.I)

RUN_FIELDS = [
    "topology", "objective_function", "seed", "file",
    "window_start_s", "window_end_s", "last_log_timestamp_s", "duration_s",
    "ocp_from_log", "sent", "received", "pdr_percent",
    "matched_requests", "unmatched_receives", "late_receives_after_window",
    "mean_delay_ms", "std_delay_ms",
    "parent_switch_events", "initial_parent_selections", "parent_changes",
    "mean_hop_count", "min_hop_count", "max_hop_count",
    "hop_count_measured_packets", "hop_count_unverified_packets",
    "hop_count_duplicate_forwarder_packets", "notes",
]
SUMMARY_FIELDS = [
    "topology", "objective_function", "runs", "seeds",
    "pdr_percent_mean", "pdr_percent_std",
    "mean_delay_ms_mean", "mean_delay_ms_std",
    "parent_changes_mean", "parent_changes_std",
    "mean_hop_count_mean", "mean_hop_count_std",
]


def parse_time_s(m: re.Match) -> float:
    return (int(m["minutes"]) * 60 + int(m["seconds"])
            + int(m["fraction"].ljust(6, "0")) / 1_000_000)


def source_id_from_ipv6(value: str) -> int | None:
    """Recognize Cooja's node-ID IPv6 address, e.g. fd00::203:3:3:3 => 3."""
    try:
        groups = [int(x, 16) for x in ipaddress.IPv6Address(value).exploded.split(":")]
    except ValueError:
        return None
    node = groups[-1]
    if (1 <= node <= 65535 and groups[-2] == node and groups[-3] == node
            and (groups[-4] & 0xFF) == (node & 0xFF)):
        return node
    return None


def topology_from_filename(path: Path) -> str:
    for label in ("line", "grid", "random"):
        if label in path.stem.lower():
            return label.capitalize()
    return "Unknown"


def of_from_filename(path: Path) -> str:
    for text in (path.parent.name, path.stem):
        if re.search(r"\bmrhof\b", text, re.I):
            return "MRHOF"
        if re.search(r"\bof0\b", text, re.I):
            return "OF0"
    return "Unknown"


def analyze(path: Path, root: Path, window_seconds: float) -> dict:
    """Analyze only 0 <= timestamp < window_seconds (Cooja simulation time)."""
    sent = received = unmatched = parents = initial = late_receives = 0
    first_event_s = last_event_s = None
    delays_ms: list[float] = []
    hops: list[int] = []
    hop_unverified = 0
    duplicate_forwarder_packets = 0
    # RPL IPv6 'going up' events, indexed by original sender node ID.
    # Counts are validated against the recipient's RPL event at receive time.
    forward_events: dict[int, deque[tuple[float, int]]] = defaultdict(deque)
    # Pending requests, keyed by originating node ID and application sequence ID.
    pending: dict[tuple[int, int], deque[float]] = defaultdict(deque)
    unknown_ips: set[str] = set()
    ocps: set[int] = set()

    with path.open("r", encoding="utf-8", errors="replace") as fh:
        for raw in fh:
            line = ANSI_RE.sub("", raw)
            stamp = TIME_NODE_RE.match(line)
            if stamp is None:
                continue
            time_s = parse_time_s(stamp)
            node = int(stamp["node"])
            if first_event_s is None or time_s < first_event_s:
                first_event_s = time_s
            if last_event_s is None or time_s > last_event_s:
                last_event_s = time_s

            # Late receptions are never counted toward the 0-300 s PDR.
            # Record them to warn about right-edge truncation.
            if time_s >= window_seconds:
                recv = RECV_RE.search(line)
                if recv:
                    client = source_id_from_ipv6(recv["ip"])
                    if client is not None:
                        queue = pending.get((client, int(recv["seq"])))
                        if queue:
                            queue.popleft()
                            late_receives += 1
                continue

            forward = FORWARD_RE.search(line)
            if forward:
                client = source_id_from_ipv6(forward["src"])
                if client is not None:
                    forward_events[client].append((time_s, node))

            ocp = OCP_RE.search(line)
            if ocp:
                ocps.add(int(ocp["ocp"]))

            send = SEND_RE.search(line)
            if send:
                sent += 1
                pending[(node, int(send["seq"]))].append(time_s)
                continue

            recv = RECV_RE.search(line)
            if recv:
                received += 1
                client = source_id_from_ipv6(recv["ip"])
                if client is None:
                    unmatched += 1
                    if len(unknown_ips) < 3:
                        unknown_ips.add(recv["ip"])
                else:
                    queue = pending.get((client, int(recv["seq"])))
                    if queue and queue[0] <= time_s:
                        send_time = queue.popleft()
                        delays_ms.append((time_s - send_time) * 1000)
                        events = forward_events[client]
                        # Remove prior forwarding traffic to bound memory use.
                        while events and events[0][0] < send_time - 0.0005:
                            events.popleft()
                        path_events = [(et, en) for et, en in events
                                       if send_time - 0.0005 <= et <= time_s + 0.0015]
                        # Require a logged RPL reception at the recipient,
                        # preventing unrelated RPL traffic from looking valid.
                        reached_root = any(en == node and abs(et - time_s) <= 0.002
                                           for et, en in path_events)
                        if reached_root:
                            hops.append(len(path_events))
                            if len({en for _, en in path_events}) != len(path_events):
                                duplicate_forwarder_packets += 1
                        else:
                            hop_unverified += 1
                    else:
                        unmatched += 1
                continue

            parent = PARENT_RE.search(line)
            if parent:
                old, new = parent["old"].strip(), parent["new"].strip()
                if old == new:
                    continue
                parents += 1
                if "null ip addr" in old.lower() or old.lower() in {"null", "none"}:
                    initial += 1

    topology = topology_from_filename(path)
    objective_function = of_from_filename(path)
    seed_match = SEED_RE.search(path.stem)
    seed = seed_match.group(1) if seed_match else "unknown"
    ocp_names = {0: "OF0", 1: "MRHOF"}

    notes: list[str] = []
    if seed == "unknown":
        notes.append("Seed unknown: original filename does not identify it")
    if last_event_s is None:
        notes.append("No timestamped mote lines parsed")
    elif last_event_s < window_seconds - 5:
        notes.append("Log may end early: last timestamp < window end by >5 s")
    if unmatched:
        notes.append(f"{unmatched} receptions could not be paired with sends")
    if unknown_ips:
        notes.append("Unknown sender IPv6 format: " + ",".join(sorted(unknown_ips)))
    if late_receives:
        notes.append(f"{late_receives} response(s) arrived after the window; not counted in PDR")
    if len(ocps) > 1:
        notes.append("WARNING: multiple OCP values found in one log")
    elif ocps and objective_function != "Unknown":
        observed_name = ocp_names.get(next(iter(ocps)), "Unknown")
        if observed_name != objective_function:
            notes.append("WARNING: Objective Function in log contradicts filename/folder")
    if not ocps:
        notes.append("RPL OCP could not be validated from log")
    if received > sent:
        notes.append("WARNING: raw received > sent within the interval")
    if hop_unverified:
        notes.append(f"Hop Count unavailable for {hop_unverified} matched UDP requests: "
                     "no matching RPL reception at destination")
    if duplicate_forwarder_packets:
        notes.append(f"WARNING: {duplicate_forwarder_packets} UDP request(s) have "
                     "repeated forwarder events; hop count is logged forward events, "
                     "not confirmed unique path length")

    matched = len(delays_ms)
    return {
        "topology": topology,
        "objective_function": objective_function,
        "seed": seed,
        "file": str(path.relative_to(root)) if path.is_relative_to(root) else str(path),
        "window_start_s": 0,
        "window_end_s": window_seconds,
        "last_log_timestamp_s": round(last_event_s, 3) if last_event_s is not None else "",
        "duration_s": round(min(last_event_s, window_seconds) - first_event_s, 3)
                      if first_event_s is not None else "",
        "ocp_from_log": ",".join(map(str, sorted(ocps))) if ocps else "",
        "sent": sent,
        "received": received,
        # Count confirmed application deliveries, avoiding duplicate/unmatched lines.
        "pdr_percent": round(100 * matched / sent, 4) if sent else "",
        "matched_requests": matched,
        "unmatched_receives": unmatched,
        "late_receives_after_window": late_receives,
        "mean_delay_ms": round(statistics.mean(delays_ms), 3) if delays_ms else "",
        "std_delay_ms": round(statistics.stdev(delays_ms), 3) if len(delays_ms) > 1 else "",
        "parent_switch_events": parents,
        "initial_parent_selections": initial,
        "parent_changes": parents - initial,
        "mean_hop_count": round(statistics.mean(hops), 4) if hops else "",
        "min_hop_count": min(hops) if hops else "",
        "max_hop_count": max(hops) if hops else "",
        "hop_count_measured_packets": len(hops),
        "hop_count_unverified_packets": hop_unverified,
        "hop_count_duplicate_forwarder_packets": duplicate_forwarder_packets,
        "notes": "; ".join(notes),
    }


def mean_std(values: list[float]) -> tuple[str, str]:
    if not values:
        return "", ""
    return (f"{statistics.mean(values):.3f}",
            f"{statistics.stdev(values):.3f}" if len(values) > 1 else "")


def summarize(rows: list[dict]) -> list[dict]:
    groups: dict[tuple[str, str], list[dict]] = defaultdict(list)
    for row in rows:
        groups[(row["topology"], row["objective_function"])].append(row)
    outputs: list[dict] = []
    for (topology, objective_function), group in sorted(groups.items()):
        result = {
            "topology": topology,
            "objective_function": objective_function,
            "runs": len(group),
            "seeds": ",".join(r["seed"] for r in group),
        }
        for key in ("pdr_percent", "mean_delay_ms", "parent_changes", "mean_hop_count"):
            values = [float(r[key]) for r in group if r[key] != ""]
            result[key + "_mean"], result[key + "_std"] = mean_std(values)
        outputs.append(result)
    return outputs


def main() -> int:
    p = argparse.ArgumentParser(description="Analyze Cooja RPL-UDP logs in a fixed time window")
    p.add_argument("--logs", type=Path, default=Path("logs/cooja"),
                   help="Input logs directory (default: logs/cooja)")
    p.add_argument("--out", type=Path, default=Path("results"),
                   help="CSV output directory (default: results)")
    p.add_argument("--window-seconds", type=float, default=300.0,
                   help="Analyze [0, N) seconds of simulation time (default: 300)")
    args = p.parse_args()
    if args.window_seconds <= 0:
        p.error("--window-seconds must be greater than zero")
    if not args.logs.is_dir():
        p.error(f"No logs directory found: {args.logs}")
    files = sorted(args.logs.rglob("*.log"))
    if not files:
        p.error(f"No .log files found under {args.logs}")

    rows = [analyze(file, Path.cwd(), args.window_seconds) for file in files]
    args.out.mkdir(parents=True, exist_ok=True)
    runs_path = args.out / "cooja_runs.csv"
    with runs_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=RUN_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    summary_path = args.out / "cooja_summary.csv"
    with summary_path.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=SUMMARY_FIELDS)
        writer.writeheader()
        writer.writerows(summarize(rows))

    print(f"Simulation-time analysis window: [0, {args.window_seconds:g}) seconds")
    print(f"{'Topology':8} {'OF':6} {'Sent':>5} {'Recv':>5} {'PDR%':>9} "
          f"{'Delay ms':>10} {'Hop':>7} {'Parent':>6} {'OCP':>4} {'LogEnd(s)':>10}")
    for row in rows:
        print(f"{row['topology']:8} {row['objective_function']:6} {row['sent']:5} "
              f"{row['received']:5} {str(row['pdr_percent']):>9} "
              f"{str(row['mean_delay_ms']):>10} {str(row['mean_hop_count']):>7} {row['parent_changes']:6} "
              f"{str(row['ocp_from_log']):>4} {str(row['last_log_timestamp_s']):>10}")
        noteworthy = [note for note in row["notes"].split("; ")
                       if "WARNING" in note or "may end early" in note
                       or "after the window" in note or "could not be paired" in note]
        for note in noteworthy:
            print("  NOTE:", note)
    print(f"\nSaved: {runs_path}\nSaved: {summary_path}")
    print("Note: existing log seeds remain 'unknown' unless recorded in filenames.")
    print("Note: Hop Count = matched RPL upward-forwarding events per delivered request;"
          " repeated forwarder events are flagged in CSV notes.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
