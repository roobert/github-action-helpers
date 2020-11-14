#!/usr/bin/env python

import argparse
import io
import json
import os
import tempfile
import zipfile
from pathlib import Path

from sh import ErrorReturnCode_1, gh


def main():
    args = _parse_args()

    print(f"==> fetching workflow\n")

    targets = args.targets
    region = args.region
    environment = args.environment
    deployment = args.deployment
    stage = args.stage

    if "infra" in targets and "k8s" in targets:
        target = "infra_and_k8s"
    elif "infra" in targets:
        target = "infra"
    elif "k8s" in targets:
        target = "k8s"

    latest = latest_runs(target, region, environment, deployment, stage)

    if not latest:
        print("waiting for run(s) to become available..", end="", flush=True)
        while not latest:
            print(".", flush=True)
            latest = latest_runs(target, region, environment, deployment, stage)
        print()

    latest_run_id = latest[0]["id"]
    latest_run = workflow_run(latest_run_id)

    print(f"workflow run url: {latest_run['html_url']}\n")

    # FIXME: if multiple runs happen at once, no real way to discern which to fetch logs for..
    if latest_run["status"] == "in_progress":
        print("waiting for run to finish..", end="", flush=True)
        while latest_run["status"] == "in_progress":
            print(".", end="", flush=True)
            latest_run = workflow_run(latest_run_id)
        print()

    if args.logs:
        print(run_log(latest_run["id"]))

    print(f"\naction exit status: {latest_run['conclusion']}")


def dispatched_runs():
    return filter(workflow_runs(), "event", "workflow_dispatch")


def latest_runs(target, region, environment, deployment, stage):
    latest_runs = filter(
        latest_incomplete_runs(),
        "workflow_name",
        f"{target} {region}-{environment}-{deployment} {stage}",
    )
    return latest_runs


def latest_incomplete_runs():
    latest_incomplete_runs = filter(dispatched_runs(), "status", "in_progress")
    return latest_incomplete_runs


def workflow(workflow_id):
    return json.loads(
        gh.api(
            f"/repos/:owner/:repo/actions/workflows/{workflow_id}",
            _env={
                **os.environ.copy(),
                "NO_COLOR": "true",
                "GITHUB_TOKEN": github_token(),
            },
        ).stdout.decode("UTF-8")
    )


def run_log(run_id):
    run_log_zip = None
    while not run_log_zip:
        try:
            run_log_zip = gh.api(
                f"/repos/:owner/:repo/actions/runs/{run_id}/logs"
            ).stdout
        except ErrorReturnCode_1:
            pass

    log = ""
    with tempfile.TemporaryDirectory() as temp_dir:
        with zipfile.ZipFile(io.BytesIO(run_log_zip), "r") as zip_file:
            zip_file.extractall(temp_dir)
            for file in Path(temp_dir).iterdir():
                if file.is_file():
                    print(f"\n==> file: {file}\n")
                    log += open(file).read()
    return log


def dump(events):
    return events
    keys = [
        "workflow_id",
        "workflow_name",
        "workflow_file",
        "id",
        "message",
        "event",
        "status",
        "conclusion",
        "logs_url",
        "html_url",
    ]
    minimised_events = [filter_keys(event, keys) for event in events]
    print(json.dumps(minimised_events))


def filter_keys(data, keys):
    return {key: data.get(key) for key in keys}


def filter(events, key, value):
    filtered = [data for data in events if data[key] == value]
    return filtered


def github_token():
    try:
        return os.environ["GITHUB_TOKEN"]
    except KeyError as error:
        raise EnvironmentError(error) from error


def workflow_run(run_id):
    run = json.loads(
        gh.api(
            f"/repos/:owner/:repo/actions/runs/{run_id}",
            _env={
                **os.environ.copy(),
                "NO_COLOR": "true",
                "GITHUB_TOKEN": github_token(),
            },
        ).stdout.decode("UTF-8")
    )
    return run


def workflow_runs():
    runs = json.loads(
        gh.api(
            "/repos/:owner/:repo/actions/runs",
            _env={
                **os.environ.copy(),
                "NO_COLOR": "true",
                "GITHUB_TOKEN": github_token(),
            },
        ).stdout.decode("UTF-8")
    )

    for workflow_run in runs["workflow_runs"]:
        workflow_json = workflow(workflow_run["workflow_id"])
        workflow_name = workflow_json["name"]
        # trim .github/workflows dir
        workflow_file = workflow_json["path"].split("/")[-1]
        workflow_run["workflow_name"] = workflow_name
        workflow_run["workflow_file"] = workflow_file

    return runs["workflow_runs"]


def _parse_args():
    parser = argparse.ArgumentParser(description="Github workflow trigger")
    parser.add_argument("-r", "--region", action="store", required=True)
    parser.add_argument("-e", "--environment", action="store", required=True)
    parser.add_argument("-d", "--deployment", action="store", required=True)
    parser.add_argument("--stage", action="store", required=True)
    parser.add_argument("--targets", action="store", required=True)
    parser.add_argument("--branch", action="store", required=True)
    parser.add_argument("--logs", action="store_true")
    return parser.parse_args()


if __name__ == "__main__":
    main()
