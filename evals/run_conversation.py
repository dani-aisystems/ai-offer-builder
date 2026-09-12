#!/usr/bin/env python3
"""Drive multi-turn eval conversations between a skill under test and a simulated user.

Why multi-turn: the skill asks questions and waits for approvals. A single prompt with every
answer pre-supplied can't test that, because a question the skill should ask would never need
asking. So each run is a real conversation:

- executor: `claude -p --safe-mode` (no CLAUDE.md, hooks or plugins), limited to the eval's
  tools, with the skill listed the way Claude Desktop lists an installed skill (name,
  description, location). The model reads SKILL.md itself when the request matches.
- simulated user: `claude -p --safe-mode --tools ""` playing the eval's persona. It answers
  only what the executor asked and follows the eval's scripted pushes.

Writes per run directory:
  outputs/        executor working directory (the deck lands here); transcript.md copied in at the end
  logs/           raw executor stream-json and simulated-user output, per turn
  transcript.md   the conversation rebuilt from the logs, including every tool call
  timing.json     tokens and durations summed from the executor's result events
  conversation.json  structured turns (tool inputs and full tool results) for the check scripts

Usage:
  python run_conversation.py --evals evals.json --plan plan.json [--workers 4]
  plan.json: [{"eval_id": 1, "config": "new_skill", "run": 1,
               "skill_dir": "<dir containing SKILL.md>", "run_dir": "<run directory>"}]
A run whose timing.json already exists is skipped, so an interrupted batch can be resumed.
"""

import argparse
import json
import re
import shutil
import subprocess
import sys
import threading
import time
import uuid
from concurrent.futures import ThreadPoolExecutor, as_completed
from pathlib import Path

EXECUTOR_MODEL = "claude-opus-5"
USER_MODEL = "claude-sonnet-5"
TOOLSETS = {
    "web": "Read,Write,Edit,Glob,Grep,WebSearch,WebFetch",
    "no_web": "Read,Write,Edit,Glob,Grep",
}
END = "[END]"
TURN_TIMEOUT_S = 45 * 60
_print_lock = threading.Lock()


def log(msg: str) -> None:
    with _print_lock:
        print(time.strftime("%H:%M:%S"), msg, flush=True)


def claude_cmd() -> list[str]:
    exe = shutil.which("claude")
    if not exe:
        sys.exit("claude CLI not found on PATH")
    if exe.lower().endswith((".cmd", ".bat")):
        return ["cmd.exe", "/c", exe]
    return [exe]


def frontmatter(skill_md: Path) -> dict:
    text = skill_md.read_text(encoding="utf-8")
    match = re.match(r"^---\r?\n(.*?)\r?\n---", text, re.DOTALL)
    fields = {}
    for line in match.group(1).splitlines() if match else []:
        if ":" in line and not line.startswith((" ", "\t")):
            key, value = line.split(":", 1)
            fields[key.strip()] = value.strip()
    return fields


def skill_listing(skill_dir: Path) -> str:
    skill_md = skill_dir / "SKILL.md"
    fm = frontmatter(skill_md)
    return (
        "Installed skills for this user:\n"
        f"- name: {fm.get('name', '')}\n"
        f"  description: {fm.get('description', '')}\n"
        f"  location: {skill_md}\n"
        "When the user's request matches a skill's description, read its SKILL.md with the Read "
        "tool before replying, then follow it.\n\n"
        "Environment: you are chatting with the user and they see only your messages. This "
        "environment has no /mnt/user-data directory and no present_files tool; save deliverable "
        "files in the current working directory and tell the user the file name."
    )


def persona_prompt(ev: dict) -> str:
    pushes = "".join(f"\n- {p}" for p in ev.get("pushes", []))
    scripted = f"\n\nSCRIPTED BEHAVIOUR{pushes}" if pushes else ""
    return (
        "You are role-playing a person who is using an AI assistant, as part of a software test. "
        "Stay in character throughout.\n\n"
        f"WHO YOU ARE AND WHAT YOU KNOW\n{ev['persona']}\n\n"
        "HOW TO REPLY\n"
        "- Reply with only the message this person would type next: no narration, labels or "
        "quotation marks around it.\n"
        "- Answer only what the assistant asked in its latest message. Keep facts it has not asked "
        "for to yourself, even when you know them.\n"
        "- Use only the facts above. For anything they don't cover, say briefly that you don't "
        "know or have no preference.\n"
        "- When the assistant presents something for approval (packages, a research log, a "
        "fictional demo client, a slide plan), approve it in a sentence unless the scripted "
        "behaviour says otherwise.\n"
        "- Keep replies short, like a busy person typing in a chat.\n"
        "- If the assistant's latest message delivers the finished result, or says it is done and "
        f"asks nothing that needs an answer, reply exactly: {END}"
        f"{scripted}"
    )


def flatten(content) -> str:
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for block in content:
            if isinstance(block, dict):
                if block.get("type") == "text":
                    parts.append(block.get("text", ""))
                elif "content" in block:
                    parts.append(flatten(block["content"]))
            else:
                parts.append(str(block))
        return "\n".join(parts)
    return "" if content is None else json.dumps(content, ensure_ascii=False)


def parse_stream(raw: str) -> dict:
    """Ordered text / tool_use / tool_result items plus the final result event of one turn."""
    items, result = [], None
    for line in raw.splitlines():
        line = line.strip()
        if not line.startswith("{"):
            continue
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        kind = event.get("type")
        if kind == "assistant":
            for block in event.get("message", {}).get("content") or []:
                if block.get("type") == "text" and block.get("text", "").strip():
                    items.append({"kind": "text", "text": block["text"]})
                elif block.get("type") == "tool_use":
                    items.append({"kind": "tool_use", "id": block.get("id"),
                                  "name": block.get("name"), "input": block.get("input") or {}})
        elif kind == "user":
            content = event.get("message", {}).get("content")
            if isinstance(content, list):
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "tool_result":
                        items.append({"kind": "tool_result", "tool_use_id": block.get("tool_use_id"),
                                      "is_error": bool(block.get("is_error")),
                                      "text": flatten(block.get("content"))})
        elif kind == "result":
            result = event
    return {"items": items, "result": result}


def executor_turn(base, message, session_id, first, tools, skill_dir, cwd, listing, log_file) -> dict:
    cmd = base + [
        "-p", "--safe-mode", "--model", EXECUTOR_MODEL,
        "--output-format", "stream-json", "--verbose",
        "--tools", tools, "--allowedTools", tools,
        "--permission-mode", "acceptEdits",
        "--add-dir", str(skill_dir),
        "--append-system-prompt", listing,
    ]
    cmd += ["--session-id", session_id] if first else ["--resume", session_id]
    proc = subprocess.run(cmd, input=message.encode("utf-8"), cwd=str(cwd),
                          capture_output=True, timeout=TURN_TIMEOUT_S)
    raw = proc.stdout.decode("utf-8", errors="replace")
    err = proc.stderr.decode("utf-8", errors="replace")
    log_file.write_text(raw + (f"\n#STDERR\n{err}" if err.strip() else ""), encoding="utf-8")
    parsed = parse_stream(raw)
    parsed["returncode"] = proc.returncode
    parsed["stderr"] = err
    return parsed


def user_turn(base, persona, history, cwd, log_file) -> str:
    convo = "\n\n".join(f"{'USER' if role == 'user' else 'ASSISTANT'}:\n{text}" for role, text in history)
    prompt = f"The conversation so far:\n\n{convo}\n\nWrite the user's next message now."
    cmd = base + ["-p", "--safe-mode", "--model", USER_MODEL, "--tools", "",
                  "--output-format", "json", "--no-session-persistence", "--system-prompt", persona]
    proc = subprocess.run(cmd, input=prompt.encode("utf-8"), cwd=str(cwd),
                          capture_output=True, timeout=600)
    raw = proc.stdout.decode("utf-8", errors="replace")
    log_file.write_text(raw, encoding="utf-8")
    try:
        return (json.loads(raw).get("result") or "").strip()
    except json.JSONDecodeError:
        return ""


def render_tool_input(name: str, inp: dict) -> str:
    if name == "Write":
        return f"{inp.get('file_path')} ({len(inp.get('content') or '')} chars)"
    if name in ("Edit", "Read"):
        return str(inp.get("file_path"))
    if name == "WebSearch":
        return f"query: {inp.get('query')}"
    if name == "WebFetch":
        return str(inp.get("url"))
    return json.dumps(inp, ensure_ascii=False)[:300]


def write_artifacts(ev, config, run_no, run_dir, outputs, turns, wall_s, status, session_id) -> None:
    lines = [f"# Transcript: eval {ev['id']} ({ev['name']}), {config}, run {run_no}", "",
             f"Status: {status}", ""]
    tool_counts, tool_errors = {}, 0
    for t in turns:
        lines += [f"## Turn {t['turn']}", "", "**User:**", "", t["user"], "", "**Assistant:**", ""]
        for item in t["items"]:
            if item["kind"] == "text":
                lines += [item["text"], ""]
            elif item["kind"] == "tool_use":
                tool_counts[item["name"]] = tool_counts.get(item["name"], 0) + 1
                lines += [f"> tool call **{item['name']}**: {render_tool_input(item['name'], item['input'])}", ""]
            elif item["kind"] == "tool_result":
                tool_errors += int(item["is_error"])
                snippet = item["text"][:240].replace("\n", " ")
                lines += [f"> result ({'ERROR' if item['is_error'] else 'ok'}, {len(item['text'])} chars): {snippet}", ""]
    transcript = "\n".join(lines)
    (run_dir / "transcript.md").write_text(transcript, encoding="utf-8")

    usage_keys = ("input_tokens", "output_tokens", "cache_creation_input_tokens", "cache_read_input_tokens")
    usage = dict.fromkeys(usage_keys, 0)
    duration_ms, cost = 0, 0.0
    for t in turns:
        result = t["result"] or {}
        for key in usage_keys:
            usage[key] += int((result.get("usage") or {}).get(key) or 0)
        duration_ms += int(result.get("duration_ms") or 0)
        cost += float(result.get("total_cost_usd") or 0)
    timing = {
        "total_tokens": sum(usage.values()),
        "duration_ms": duration_ms,
        "total_duration_seconds": round(duration_ms / 1000, 1),
        "wall_clock_seconds": round(wall_s, 1),
        "executor_turns": len(turns),
        "token_breakdown": usage,
        "reported_cost_usd": round(cost, 4),
        "session_id": session_id,
        "status": status,
    }
    (run_dir / "timing.json").write_text(json.dumps(timing, indent=2), encoding="utf-8")

    files = [p for p in outputs.iterdir() if p.is_file() and p.name not in ("transcript.md", "metrics.json")]
    metrics = {
        "tool_calls": tool_counts,
        "total_tool_calls": sum(tool_counts.values()),
        "total_steps": len(turns),
        "files_created": [p.name for p in files],
        "errors_encountered": tool_errors,
        "output_chars": sum(p.stat().st_size for p in files),
        "transcript_chars": len(transcript),
    }
    (outputs / "metrics.json").write_text(json.dumps(metrics, indent=2), encoding="utf-8")
    conversation = [{"turn": t["turn"], "user": t["user"], "items": t["items"]} for t in turns]
    (run_dir / "conversation.json").write_text(json.dumps(conversation, ensure_ascii=False, indent=1), encoding="utf-8")
    shutil.copyfile(run_dir / "transcript.md", outputs / "transcript.md")


def run_one(base, ev, config, run_no, skill_dir: Path, run_dir: Path) -> str:
    tag = f"eval-{ev['id']} {config} run-{run_no}"
    if (run_dir / "timing.json").exists():
        return "skipped (already done)"
    outputs, logs = run_dir / "outputs", run_dir / "logs"
    outputs.mkdir(parents=True, exist_ok=True)
    logs.mkdir(parents=True, exist_ok=True)
    listing = skill_listing(skill_dir)
    tools = TOOLSETS[ev.get("tools", "web")]
    persona = persona_prompt(ev)
    session_id = str(uuid.uuid4())
    history, turns = [], []
    message = ev["prompt"]
    started = time.time()
    status = "max turns reached"
    for turn in range(1, ev.get("max_turns", 12) + 1):
        history.append(("user", message))
        parsed = executor_turn(base, message, session_id, turn == 1, tools, skill_dir, outputs,
                               listing, logs / f"executor-{turn:02d}.jsonl")
        texts = [i["text"] for i in parsed["items"] if i["kind"] == "text"]
        reply = "\n\n".join(texts) or ((parsed["result"] or {}).get("result") or "")
        turns.append({"turn": turn, "user": message, "items": parsed["items"], "result": parsed["result"]})
        history.append(("assistant", reply))
        n_tools = sum(1 for i in parsed["items"] if i["kind"] == "tool_use")
        log(f"[{tag}] turn {turn}: {n_tools} tool calls, reply {len(reply)} chars")
        if parsed["result"] is None or parsed["result"].get("is_error"):
            status = f"executor error on turn {turn} (rc={parsed['returncode']}): {parsed['stderr'][-300:]}"
            break
        nxt = user_turn(base, persona, history, logs, logs / f"user-{turn:02d}.json")
        if not nxt:
            status = f"simulated user returned nothing on turn {turn}"
            break
        if nxt.startswith(END):
            status = "completed"
            break
        message = nxt
    write_artifacts(ev, config, run_no, run_dir, outputs, turns, time.time() - started, status, session_id)
    return status


def main() -> None:
    ap = argparse.ArgumentParser(description="Run multi-turn skill evals with a simulated user.")
    ap.add_argument("--evals", type=Path, required=True)
    ap.add_argument("--plan", type=Path, required=True)
    ap.add_argument("--workers", type=int, default=4)
    args = ap.parse_args()
    evals = {e["id"]: e for e in json.loads(args.evals.read_text(encoding="utf-8"))["evals"]}
    plan = json.loads(args.plan.read_text(encoding="utf-8"))
    base = claude_cmd()
    log(f"{len(plan)} runs, {args.workers} workers, claude at {base[-1]}")
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {
            pool.submit(run_one, base, evals[p["eval_id"]], p["config"], p["run"],
                        Path(p["skill_dir"]), Path(p["run_dir"])): p
            for p in plan
        }
        for future in as_completed(futures):
            p = futures[future]
            try:
                status = future.result()
            except Exception as exc:  # keep the batch going; the failed run is reported
                status = f"exception: {exc!r}"
            log(f"[done] eval-{p['eval_id']} {p['config']} run-{p['run']}: {status}")


if __name__ == "__main__":
    main()
