"""RUNE CLI: bootstrap, check, endorse, revoke, triage, list, mcp."""

from __future__ import annotations

import argparse
import json
import os
import sys
from typing import Any

from rune.gate import Gate
from rune.jethro import classify_triage, triage_action
from rune.ledger import EndorsementLedger


def _print(data: Any) -> None:
    print(json.dumps(data, indent=2, ensure_ascii=False))


def cmd_bootstrap(args: argparse.Namespace) -> int:
    gate = Gate(EndorsementLedger(args.ledger))
    result = gate.bootstrap_human_verifier(args.verifier_id, actor=args.actor)
    _print(result)
    return 0


def cmd_check(args: argparse.Namespace) -> int:
    gate = Gate(EndorsementLedger(args.ledger))
    decision = gate.check(
        args.subject_type,
        args.reference,
        actor=args.actor,
        consensus_claimed=args.consensus_claimed,
    )
    _print(decision.to_dict())
    return 0 if decision.allowed else 2


def cmd_endorse(args: argparse.Namespace) -> int:
    if not args.confirm and not args.pending and not args.reject:
        print(
            "error: pass --confirm (human endorse), --pending, or --reject",
            file=sys.stderr,
        )
        return 1
    gate = Gate(EndorsementLedger(args.ledger))
    evidence = args.evidence or []
    record = gate.request_endorsement(
        args.subject_type,
        args.reference,
        method=args.method,
        actor=args.actor,
        evidence_refs=evidence,
        confirm=bool(args.confirm),
        reject=bool(args.reject),
        verifier_id=args.verifier_id,
        expires_at=args.expires_at,
    )
    _print(record.to_dict())
    return 0


def cmd_revoke(args: argparse.Namespace) -> int:
    gate = Gate(EndorsementLedger(args.ledger))
    try:
        record = gate.revoke(args.endorsement_id, actor=args.actor, reason=args.reason)
    except KeyError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    _print(record.to_dict())
    return 0


def cmd_list(args: argparse.Namespace) -> int:
    ledger = EndorsementLedger(args.ledger)
    rows = ledger.list_rows(limit=args.limit)
    _print(rows)
    return 0


def cmd_triage(args: argparse.Namespace) -> int:
    color = classify_triage(
        args.subject_type,
        consensus_claimed=args.consensus_claimed,
        surprise_channel=args.surprise_channel,
        evidence_complete=not args.incomplete_evidence,
        has_endorsement=args.has_endorsement,
    )
    _print({"jethro_color": color, "action": triage_action(color)})
    return 0


def cmd_mcp(args: argparse.Namespace) -> int:
    from rune.mcp_server import run_mcp

    run_mcp(ledger_path=args.ledger)
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="rune",
        description="RUNE — Runtime Unified Network Endorsement gate and ledger",
    )
    parser.add_argument(
        "--ledger",
        default=None,
        help="JSONL ledger path (default: RUNE_LEDGER_PATH or ./data/endorsement_ledger.jsonl)",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    p_boot = sub.add_parser("bootstrap", help="Bootstrap human verifier (SSE/Robyn)")
    p_boot.add_argument("--verifier-id", default="sse-robyn")
    p_boot.add_argument("--actor", default="owner")
    p_boot.set_defaults(func=cmd_bootstrap)

    p_check = sub.add_parser("check", help="Fail-closed gate check")
    p_check.add_argument("--subject-type", required=True)
    p_check.add_argument("--reference", required=True)
    p_check.add_argument("--actor", default="cli")
    p_check.add_argument(
        "--consensus-claimed",
        action="store_true",
        help="Treat as multi-agent consensus claim (always rejected for high-risk)",
    )
    p_check.set_defaults(func=cmd_check)

    p_end = sub.add_parser("endorse", help="Request or confirm endorsement")
    p_end.add_argument("--subject-type", required=True)
    p_end.add_argument("--reference", required=True)
    p_end.add_argument("--method", required=True)
    p_end.add_argument("--actor", default="cli")
    p_end.add_argument("--verifier-id", default=None)
    p_end.add_argument("--evidence", action="append", default=[])
    p_end.add_argument("--expires-at", default=None)
    g = p_end.add_mutually_exclusive_group()
    g.add_argument("--confirm", action="store_true", help="Human verifier confirms ENDORSED")
    g.add_argument("--pending", action="store_true", help="Create PENDING request")
    g.add_argument("--reject", action="store_true", help="Human verifier rejects")
    p_end.set_defaults(func=cmd_endorse)

    p_rev = sub.add_parser("revoke", help="Revoke an endorsement")
    p_rev.add_argument("--endorsement-id", required=True)
    p_rev.add_argument("--reason", required=True)
    p_rev.add_argument("--actor", default="cli")
    p_rev.set_defaults(func=cmd_revoke)

    p_list = sub.add_parser("list", help="List recent ledger rows")
    p_list.add_argument("--limit", type=int, default=20)
    p_list.set_defaults(func=cmd_list)

    p_tri = sub.add_parser("triage", help="Jethro Green/Yellow/Red classification")
    p_tri.add_argument("--subject-type", required=True)
    p_tri.add_argument("--consensus-claimed", action="store_true")
    p_tri.add_argument("--surprise-channel", action="store_true")
    p_tri.add_argument("--incomplete-evidence", action="store_true")
    p_tri.add_argument("--has-endorsement", action="store_true")
    p_tri.set_defaults(func=cmd_triage)

    p_mcp = sub.add_parser("mcp", help="Run thin MCP server (request/verify/list)")
    p_mcp.set_defaults(func=cmd_mcp)

    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    if args.ledger:
        os.environ["RUNE_LEDGER_PATH"] = args.ledger
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
