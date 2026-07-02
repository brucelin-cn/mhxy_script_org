import argparse

from scheduler import SchedulerRunner


def main() -> None:
    parser = argparse.ArgumentParser(description="MHXY scheduler")
    parser.add_argument(
        "-c",
        "--config",
        default="resources/scheduler/scheduler.json",
        type=str,
        help="Scheduler config json path",
    )
    args = parser.parse_args()
    SchedulerRunner.from_file(args.config).run()


if __name__ == "__main__":
    main()
