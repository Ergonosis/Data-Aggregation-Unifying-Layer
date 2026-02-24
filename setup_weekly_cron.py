#!/usr/bin/env python3
import argparse
import subprocess
import sys
from pathlib import Path
from dotenv import dotenv_values

MARKER = "# data-aggregation-weekly-sync"


def run(cmd: list[str], input_text: str | None = None) -> subprocess.CompletedProcess:
    return subprocess.run(
        cmd,
        input=input_text,
        text=True,
        capture_output=True,
        check=False,
    )


def get_current_crontab() -> str:
    result = run(["crontab", "-l"])
    if result.returncode == 0:
        return result.stdout
    stderr = (result.stderr or "").lower()
    if "no crontab for" in stderr:
        return ""
    raise RuntimeError(f"Unable to read crontab: {result.stderr.strip()}")


def install_crontab(contents: str) -> None:
    result = run(["crontab", "-"], input_text=contents)
    if result.returncode != 0:
        raise RuntimeError(f"Unable to write crontab: {result.stderr.strip()}")


def build_job_line(repo_root: Path, python_exec: str, weekday: str, hour: int, minute: int) -> str:
    log_dir = repo_root / "records" / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    log_file = log_dir / "weekly_sync.log"
    return (
        f"{minute} {hour} * * {weekday} "
        f"cd {repo_root} && {python_exec} sync_data.py >> {log_file} 2>&1 {MARKER}"
    )


def normalize_weekday(day: str) -> str:
    mapping = {
        "sun": "0",
        "mon": "1",
        "tue": "2",
        "wed": "3",
        "thu": "4",
        "fri": "5",
        "sat": "6",
    }
    key = day.strip().lower()[:3]
    if key not in mapping:
        raise ValueError("weekday must be one of: sun, mon, tue, wed, thu, fri, sat")
    return mapping[key]


def remove_existing_job(lines: list[str]) -> list[str]:
    return [line for line in lines if MARKER not in line]


def resolve_python_exec(repo_root: Path, provided: str | None) -> str:
    if provided:
        return provided
    venv_python = repo_root / "venv" / "bin" / "python"
    dot_venv_python = repo_root / ".venv" / "bin" / "python"
    if venv_python.exists():
        return str(venv_python)
    if dot_venv_python.exists():
        return str(dot_venv_python)
    return sys.executable


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Install or remove weekly cron schedule for sync_data.py."
    )
    parser.add_argument(
        "--remove",
        action="store_true",
        help="Remove existing scheduled weekly sync job.",
    )
    parser.add_argument(
        "--weekday",
        default=None,
        help="Day to run weekly sync (sun, mon, tue, wed, thu, fri, sat). "
        "Default: SYNC_WEEKDAY in .env, else mon",
    )
    parser.add_argument(
        "--hour",
        type=int,
        default=None,
        help="Hour in 24h local time. Default: SYNC_HOUR in .env, else 9",
    )
    parser.add_argument(
        "--minute",
        type=int,
        default=None,
        help="Minute. Default: SYNC_MINUTE in .env, else 0",
    )
    parser.add_argument(
        "--python",
        default=None,
        help="Python executable path for cron job. "
        "Default: SYNC_PYTHON_PATH in .env, then ./venv/bin/python, then ./.venv/bin/python, then current python.",
    )
    args = parser.parse_args()

    repo_root = Path(__file__).resolve().parent
    env = dotenv_values(repo_root / ".env")

    weekday_raw = args.weekday or env.get("SYNC_WEEKDAY") or "mon"
    hour_raw = args.hour if args.hour is not None else env.get("SYNC_HOUR", "9")
    minute_raw = args.minute if args.minute is not None else env.get("SYNC_MINUTE", "0")

    try:
        hour = int(hour_raw)
        minute = int(minute_raw)
    except (TypeError, ValueError):
        raise ValueError("SYNC_HOUR and SYNC_MINUTE must be valid integers")

    if not (0 <= hour <= 23):
        raise ValueError("hour must be between 0 and 23")
    if not (0 <= minute <= 59):
        raise ValueError("minute must be between 0 and 59")

    weekday = normalize_weekday(str(weekday_raw))
    python_exec = resolve_python_exec(repo_root, args.python or env.get("SYNC_PYTHON_PATH"))

    current = get_current_crontab().splitlines()
    updated = remove_existing_job(current)

    if args.remove:
        install_crontab("\n".join(updated) + ("\n" if updated else ""))
        print("Removed weekly sync cron job.")
        return 0

    job_line = build_job_line(
        repo_root=repo_root,
        python_exec=python_exec,
        weekday=weekday,
        hour=hour,
        minute=minute,
    )
    updated.append(job_line)
    install_crontab("\n".join(updated) + "\n")
    print(
        "Installed weekly sync cron job: "
        f"{str(weekday_raw).lower()} at {hour:02d}:{minute:02d} local time."
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
