import argparse

from scheduler import SchedulerRunner
from scheduler.env_check import check_dependencies
from scheduler.env_check import format_dependency_report
from scheduler.env_check import missing_packages


def main() -> None:
    parser = argparse.ArgumentParser(description="MHXY scheduler")
    parser.add_argument(
        "-c",
        "--config",
        default="resources/scheduler/scheduler.json",
        type=str,
        help="Scheduler config json path",
    )
    parser.add_argument(
        "--check-env",
        action="store_true",
        help="Check required runtime dependencies and exit",
    )
    args = parser.parse_args()
    if args.check_env:
        results = check_dependencies()
        print(format_dependency_report(results))
        raise SystemExit(1 if missing_packages(results) else 0)
    SchedulerRunner.from_file(args.config).run()


if __name__ == "__main__":
    main()
