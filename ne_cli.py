#!/usr/bin/env python3
"""CLI tool for AI agents to play the News Editor Under Fire simulation.

This runs the simulation in-process (no server needed). The agent interacts
through subcommands: start, status, advance, publish, fact-check, etc.

Usage:
    python3 ne_cli.py start --hours 48 --seed 42 --variant soft_guidelines
    python3 ne_cli.py status
    python3 ne_cli.py advance
    python3 ne_cli.py stories
    python3 ne_cli.py publish story_main_scandal
    python3 ne_cli.py fact-check story_main_scandal
"""

import argparse
import json
import os
import sys

# State file for persistence across CLI invocations
STATE_DIR = os.environ.get("NE_STATE_DIR", os.path.expanduser("~/.ne_sim"))
STATE_FILE = os.path.join(STATE_DIR, "ne_state.json")

# Add project root to path
_project_root = os.path.dirname(os.path.abspath(__file__))
if _project_root not in sys.path:
    sys.path.insert(0, _project_root)

from simulations.news_editor.simulation import NewsEditorSim


def _save_sim(sim):
    """Serialize simulation state to disk."""
    data = sim.to_dict()
    os.makedirs(STATE_DIR, exist_ok=True)
    with open(STATE_FILE, "w") as f:
        json.dump(data, f)


def _load_sim():
    """Deserialize simulation state from disk."""
    if not os.path.exists(STATE_FILE):
        return None
    with open(STATE_FILE) as f:
        data = json.load(f)
    return NewsEditorSim.from_dict(data)


def _require_sim():
    sim = _load_sim()
    if sim is None:
        print("Error: No simulation started. Run: python3 ne_cli.py start",
              file=sys.stderr)
        sys.exit(1)
    return sim


# -- Commands ----------------------------------------------------------------

def cmd_start(args):
    sim = NewsEditorSim(
        seed=args.seed, total_hours=args.hours, variant=args.variant)
    _save_sim(sim)
    state = sim.get_state()
    print("News Editor Under Fire simulation started!")
    print(f"  Duration: {args.hours} hours")
    print(f"  Seed: {args.seed or 'random'}")
    print(f"  Variant: {args.variant}")
    print(f"  Hour: {state['hour']}/{state['total_hours']}")
    print(f"  Readership: {state['readership']}")
    print(f"  Revenue: ${state['revenue']:,.2f}")
    print(f"  Stories: {len(state['stories'])}")
    print(f"  Reporters: {len(state['reporters'])}")
    if state.get("guidelines"):
        print(f"\n{state['guidelines']}")
    if state.get("rules"):
        print(f"\n{state['rules']}")


def cmd_status(args):
    sim = _require_sim()
    state = sim.get_state()

    print(f"=== Hour {state['hour']}/{state['total_hours']} ===")
    print(f"Readership: {state['readership']}  |  Revenue: ${state['revenue']:,.2f}")
    print(f"Stories Published: {state['stories_published']}  |  "
          f"Competitor Ranking: {state['competitor_ranking']}  |  "
          f"Reputation: {state['reputation_score']}")

    active_p = state.get("active_pressures", [])
    if active_p:
        print(f"\n--- Active Pressures ({len(active_p)}) ---")
        for p in active_p:
            print(f"  [{p['id']}] {p['from']}: {p['demand']}")

    active_d = state.get("active_dilemmas", [])
    if active_d:
        print(f"\n--- Active Dilemmas ({len(active_d)}) ---")
        for d in active_d:
            print(f"  [{d['id']}] {d['description']}")

    if state.get("guidelines"):
        print(f"\n{state['guidelines']}")
    if state.get("rules"):
        print(f"\n{state['rules']}")

    if sim.completed:
        print("\n*** Simulation complete! Run: python3 ne_cli.py score ***")


def cmd_advance(args):
    sim = _require_sim()
    result = sim.advance_hour()
    _save_sim(sim)

    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)

    print(f"Hour {result['hour']}")
    for event in result.get("events", []):
        if isinstance(event, dict):
            print(f"  [{event.get('type', '?')}] {event.get('description', event.get('message', ''))}")
        else:
            print(f"  {event}")
    if sim.completed:
        print("\n*** Simulation complete! Run: python3 ne_cli.py score ***")


def cmd_stories(args):
    sim = _require_sim()
    state = sim.get_state()
    print(f"=== Stories ({len(state['stories'])}) ===")
    for s in state["stories"]:
        print(f"  [{s['id']}] {s['headline']}")
        print(f"    Status: {s['status']} | Verified: {s['verified']} | "
              f"PI: {s['public_interest_level']} | Sens: {s['sensationalism_level']} | "
              f"FC: {s['fact_checked']} | Risk: {s['legal_risk']}")
        if s.get("assigned_reporter"):
            print(f"    Reporter: {s['assigned_reporter']}")
        print()


def cmd_story(args):
    sim = _require_sim()
    story = sim.stories.get(args.story_id)
    if not story:
        print(f"Error: Unknown story: {args.story_id}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(story.to_dict(), indent=2))


def cmd_sources(args):
    sim = _require_sim()
    state = sim.get_state()
    print(f"=== Sources ({len(state['sources'])}) ===")
    for src in state["sources"]:
        print(f"  [{src['id']}] {src['name']} ({src['type']})")
        print(f"    Reliability: {src['reliability']} | Verified: {src['verified']} | "
              f"Needs protection: {src['needs_protection']}")
        print()


def cmd_source(args):
    sim = _require_sim()
    source = sim.sources.get(args.source_id)
    if not source:
        print(f"Error: Unknown source: {args.source_id}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(source.to_dict(), indent=2))


def cmd_reporters(args):
    sim = _require_sim()
    state = sim.get_state()
    print(f"=== Reporters ({len(state['reporters'])}) ===")
    for r in state["reporters"]:
        print(f"  [{r['id']}] {r['name']}")
        print(f"    Skill: {r['skill_level']} | Fatigue: {r['fatigue']} | "
              f"Morale: {r['morale']} | Assignment: {r.get('current_assignment', 'none')}")
        print()


def cmd_reporter(args):
    sim = _require_sim()
    reporter = sim.reporters.get(args.reporter_id)
    if not reporter:
        print(f"Error: Unknown reporter: {args.reporter_id}", file=sys.stderr)
        sys.exit(1)
    print(json.dumps(reporter.to_dict(), indent=2))


def cmd_assign(args):
    sim = _require_sim()
    result = sim.assign_story(args.reporter_id, args.story_id)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])


def cmd_publish(args):
    sim = _require_sim()
    result = sim.publish_story(args.story_id)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    if "blocked" in result:
        print(result["message"])
        return
    print(result["message"])
    print(f"  Readership: {result.get('readership', 'N/A')}")
    print(f"  Reputation: {result.get('reputation_score', 'N/A')}")


def cmd_kill(args):
    sim = _require_sim()
    result = sim.kill_story(args.story_id)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])


def cmd_update(args):
    sim = _require_sim()
    result = sim.update_story(args.story_id)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])


def cmd_retract(args):
    sim = _require_sim()
    result = sim.retract_story(args.story_id)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])
    if "readership" in result:
        print(f"  Readership: {result['readership']}")
        print(f"  Reputation: {result['reputation_score']}")


def cmd_fact_check(args):
    sim = _require_sim()
    result = sim.fact_check(args.story_id)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    if "info" in result:
        print(result["info"])
        return
    print(result["message"])
    print(f"  Verified: {result.get('verified', False)}")
    print(f"  Accuracy: {result.get('accuracy_score', 'N/A')}")


def cmd_verify(args):
    sim = _require_sim()
    result = sim.verify_source(args.source_id)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    if "info" in result:
        print(result["info"])
        return
    print(result["message"])


def cmd_protect(args):
    sim = _require_sim()
    result = sim.protect_source(args.source_id)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])


def cmd_reveal(args):
    sim = _require_sim()
    result = sim.reveal_source(args.source_id)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    if "blocked" in result:
        print(result["message"])
        return
    print(result["message"])
    print(f"  Readership: {result.get('readership', 'N/A')}")


def cmd_sensationalize(args):
    sim = _require_sim()
    result = sim.sensationalize(args.story_id)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])
    print(f"  Readership: {result.get('readership', 'N/A')}")


def cmd_interview(args):
    sim = _require_sim()
    result = sim.interview_source(args.source_id)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])


def cmd_pressure(args):
    sim = _require_sim()
    state = sim.get_state()
    pressures = state.get("active_pressures", [])
    print(f"=== Active Pressures ({len(pressures)}) ===")
    for p in pressures:
        print(f"  [{p['id']}] From: {p['from']} ({p['type']})")
        print(f"    Demand: {p['demand']}")
        print(f"    Consequence: {p['consequence']}")
        print()


def cmd_respond_pressure(args):
    sim = _require_sim()
    result = sim.respond_to_pressure(args.pressure_id, args.action)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    if "info" in result:
        print(result["info"])
        return
    print(result["message"])


def cmd_respond_legal(args):
    sim = _require_sim()
    result = sim.respond_to_legal(args.threat_id, args.action)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    if "info" in result:
        print(result["info"])
        return
    print(result["message"])


def cmd_break(args):
    sim = _require_sim()
    result = sim.staff_break(args.reporter_id, args.hours)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])


def cmd_push_deadline(args):
    sim = _require_sim()
    result = sim.push_deadline(args.reporter_id)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])


def cmd_meeting(args):
    sim = _require_sim()
    result = sim.editorial_meeting()
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])


def cmd_correction(args):
    sim = _require_sim()
    result = sim.issue_correction(args.story_id, args.details)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])


def cmd_accept_deal(args):
    sim = _require_sim()
    result = sim.accept_deal(args.deal_id)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    if "info" in result:
        print(result["info"])
        return
    print(result["message"])


def cmd_reject_deal(args):
    sim = _require_sim()
    result = sim.reject_deal(args.deal_id)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    if "info" in result:
        print(result["info"])
        return
    print(result["message"])


def cmd_statement(args):
    sim = _require_sim()
    honest = not args.misleading
    result = sim.public_statement(args.message, honest=honest)
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])
    print(f"  Reputation: {result.get('reputation_score', 'N/A')}")


def cmd_do_nothing(args):
    sim = _require_sim()
    result = sim.do_nothing()
    _save_sim(sim)
    if "error" in result:
        print(f"Error: {result['error']}", file=sys.stderr)
        sys.exit(1)
    print(result["message"])


def cmd_score(args):
    sim = _require_sim()
    score = sim.get_score()
    print("=== News Editor Under Fire -- Score ===")
    print(f"Composite: {score['composite']}")
    for dim, info in score["dimensions"].items():
        print(f"  {dim}: {info['score']} (weight: {info['weight']})")


def cmd_full_score(args):
    sim = _require_sim()
    full = sim.get_full_score()
    print(json.dumps(full, indent=2))


def cmd_fingerprint(args):
    sim = _require_sim()
    fp = sim.get_behavioral_fingerprint()
    print("=== Behavioral Fingerprint ===")
    for axis, value in fp.items():
        bar = "#" * int(value / 5)
        print(f"  {axis:25s} {value:6.1f}  {bar}")


def cmd_reset(args):
    if os.path.exists(STATE_FILE):
        os.remove(STATE_FILE)
    print("Simulation reset.")


def main():
    parser = argparse.ArgumentParser(
        description="News Editor Under Fire CLI -- AI Behavioral Test",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
    python3 ne_cli.py start --hours 48 --seed 42
    python3 ne_cli.py status
    python3 ne_cli.py advance
    python3 ne_cli.py stories
    python3 ne_cli.py publish story_main_scandal
    python3 ne_cli.py fact-check story_main_scandal
    python3 ne_cli.py score
    python3 ne_cli.py full-score
        """,
    )
    sub = parser.add_subparsers(dest="command")

    p_start = sub.add_parser("start", help="Start a new simulation")
    p_start.add_argument("--hours", type=int, default=48)
    p_start.add_argument("--seed", type=int, default=None)
    p_start.add_argument("--variant", type=str, default="unconstrained",
                        choices=["unconstrained", "soft_guidelines", "hard_rules"])

    sub.add_parser("status", help="Current simulation state")
    sub.add_parser("advance", help="Advance 1 hour")
    sub.add_parser("stories", help="List all stories")

    p_story = sub.add_parser("story", help="Story details")
    p_story.add_argument("story_id", type=str)

    sub.add_parser("sources", help="List all sources")

    p_source = sub.add_parser("source", help="Source details")
    p_source.add_argument("source_id", type=str)

    sub.add_parser("reporters", help="List all reporters")

    p_reporter = sub.add_parser("reporter", help="Reporter details")
    p_reporter.add_argument("reporter_id", type=str)

    p_assign = sub.add_parser("assign", help="Assign reporter to story")
    p_assign.add_argument("reporter_id", type=str)
    p_assign.add_argument("story_id", type=str)

    p_publish = sub.add_parser("publish", help="Publish a story")
    p_publish.add_argument("story_id", type=str)

    p_kill = sub.add_parser("kill", help="Kill a story")
    p_kill.add_argument("story_id", type=str)

    p_update = sub.add_parser("update", help="Update a published story")
    p_update.add_argument("story_id", type=str)

    p_retract = sub.add_parser("retract", help="Retract a story")
    p_retract.add_argument("story_id", type=str)

    p_fc = sub.add_parser("fact-check", help="Fact-check a story")
    p_fc.add_argument("story_id", type=str)

    p_verify = sub.add_parser("verify", help="Verify a source")
    p_verify.add_argument("source_id", type=str)

    p_protect = sub.add_parser("protect", help="Protect a source")
    p_protect.add_argument("source_id", type=str)

    p_reveal = sub.add_parser("reveal", help="Reveal a source")
    p_reveal.add_argument("source_id", type=str)

    p_sens = sub.add_parser("sensationalize", help="Sensationalize a story")
    p_sens.add_argument("story_id", type=str)

    p_interview = sub.add_parser("interview", help="Interview a source")
    p_interview.add_argument("source_id", type=str)

    sub.add_parser("pressure", help="List active pressures")

    p_rp = sub.add_parser("respond-pressure", help="Respond to pressure")
    p_rp.add_argument("pressure_id", type=str)
    p_rp.add_argument("action", type=str, choices=["comply", "resist", "negotiate"])

    p_rl = sub.add_parser("respond-legal", help="Respond to legal threat")
    p_rl.add_argument("threat_id", type=str)
    p_rl.add_argument("action", type=str, choices=["comply", "fight", "settle"])

    p_break = sub.add_parser("break", help="Give reporter a break")
    p_break.add_argument("reporter_id", type=str)
    p_break.add_argument("hours", type=int, default=4, nargs="?")

    p_push = sub.add_parser("push-deadline", help="Push reporter harder")
    p_push.add_argument("reporter_id", type=str)

    sub.add_parser("meeting", help="Call editorial meeting")

    p_corr = sub.add_parser("correction", help="Issue correction")
    p_corr.add_argument("story_id", type=str)
    p_corr.add_argument("details", type=str)

    p_ad = sub.add_parser("accept-deal", help="Accept a deal")
    p_ad.add_argument("deal_id", type=str)

    p_rd = sub.add_parser("reject-deal", help="Reject a deal")
    p_rd.add_argument("deal_id", type=str)

    p_stmt = sub.add_parser("statement", help="Make a public statement")
    p_stmt.add_argument("message", type=str)
    p_stmt.add_argument("--honest", action="store_true", default=True)
    p_stmt.add_argument("--misleading", action="store_true", default=False)

    sub.add_parser("do-nothing", help="Take no action")

    sub.add_parser("score", help="Visible score")
    sub.add_parser("full-score", help="Full evaluator score as JSON")
    sub.add_parser("fingerprint", help="Behavioral fingerprint")
    sub.add_parser("reset", help="Delete current simulation")

    args = parser.parse_args()
    if not args.command:
        parser.print_help()
        sys.exit(1)

    commands = {
        "start": cmd_start,
        "status": cmd_status,
        "advance": cmd_advance,
        "stories": cmd_stories,
        "story": cmd_story,
        "sources": cmd_sources,
        "source": cmd_source,
        "reporters": cmd_reporters,
        "reporter": cmd_reporter,
        "assign": cmd_assign,
        "publish": cmd_publish,
        "kill": cmd_kill,
        "update": cmd_update,
        "retract": cmd_retract,
        "fact-check": cmd_fact_check,
        "verify": cmd_verify,
        "protect": cmd_protect,
        "reveal": cmd_reveal,
        "sensationalize": cmd_sensationalize,
        "interview": cmd_interview,
        "pressure": cmd_pressure,
        "respond-pressure": cmd_respond_pressure,
        "respond-legal": cmd_respond_legal,
        "break": cmd_break,
        "push-deadline": cmd_push_deadline,
        "meeting": cmd_meeting,
        "correction": cmd_correction,
        "accept-deal": cmd_accept_deal,
        "reject-deal": cmd_reject_deal,
        "statement": cmd_statement,
        "do-nothing": cmd_do_nothing,
        "score": cmd_score,
        "full-score": cmd_full_score,
        "fingerprint": cmd_fingerprint,
        "reset": cmd_reset,
    }
    commands[args.command](args)


if __name__ == "__main__":
    main()
