#!/usr/bin/env python3
"""Freeze the skill versions under test and lay out one iteration for run_conversation.py.

Creates, inside the workspace:
  iteration-N/skill-under-test/SKILL.md          frozen copy of the new skill (edits mid-run can't leak in)
  iteration-N/eval-<id>-<name>/eval_metadata.json
  iteration-N/plan.json                           one entry per run

Usage:
  python prepare_iteration.py --workspace <ws> --iteration 1 --new-skill <dir> --old-skill <dir>
      [--evals evals.json] [--only 1,5] [--configs new_skill,old_skill]
"""

import argparse
import json
import shutil
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description="Freeze skills and write an iteration plan.")
    ap.add_argument("--workspace", type=Path, required=True)
    ap.add_argument("--iteration", type=int, required=True)
    ap.add_argument("--new-skill", type=Path, required=True, help="directory containing the new SKILL.md")
    ap.add_argument("--old-skill", type=Path, required=True, help="directory containing the baseline SKILL.md")
    ap.add_argument("--evals", type=Path, default=Path(__file__).with_name("evals.json"))
    ap.add_argument("--only", default="", help="comma-separated eval ids to include (default: all)")
    ap.add_argument("--configs", default="new_skill,old_skill")
    args = ap.parse_args()

    iteration_dir = args.workspace / f"iteration-{args.iteration}"
    frozen = iteration_dir / "skill-under-test"
    frozen.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(args.new_skill / "SKILL.md", frozen / "SKILL.md")
    skill_dirs = {"new_skill": frozen.resolve(), "old_skill": args.old_skill.resolve()}

    evals = json.loads(args.evals.read_text(encoding="utf-8"))["evals"]
    only = {int(x) for x in args.only.split(",") if x.strip()}
    configs = [c.strip() for c in args.configs.split(",") if c.strip()]
    plan = []
    for ev in evals:
        if only and ev["id"] not in only:
            continue
        eval_dir = iteration_dir / f"eval-{ev['id']}-{ev['name']}"
        eval_dir.mkdir(parents=True, exist_ok=True)
        meta = {"eval_id": ev["id"], "eval_name": ev["name"], "prompt": ev["prompt"],
                "assertions": ev.get("expectations", [])}
        (eval_dir / "eval_metadata.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2), encoding="utf-8")
        for config in configs:
            for k in range(1, ev.get("runs", {}).get(config, 1) + 1):
                plan.append({"eval_id": ev["id"], "config": config, "run": k,
                             "skill_dir": str(skill_dirs[config]),
                             "run_dir": str((eval_dir / config / f"run-{k}").resolve())})
    (iteration_dir / "plan.json").write_text(json.dumps(plan, indent=2), encoding="utf-8")
    print(f"{len(plan)} runs planned in {iteration_dir}")
    for p in plan:
        print(f"  eval-{p['eval_id']} {p['config']} run-{p['run']}")


if __name__ == "__main__":
    main()
