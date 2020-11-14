#!/usr/bin/env python

import argparse
import json
from tempfile import NamedTemporaryFile

from sh import gh


def main():
    args = _parse_args()
    workflow = _workflow(args)

    _trigger_workflow(
        args.region, args.environment, args.deployment, workflow, args.branch
    )


def _workflow(args):
    targets = args.targets.split("\n")
    stage = args.stage
    region = args.region
    environment = args.environment
    deployment = args.deployment

    if "k8s_and_infra" in targets:
        workflow = f"infra_and_k8s-{region}-{environment}-{deployment}-{stage}.yaml"
    elif "infra" in targets and "k8s" in targets:
        workflow = f"infra_and_k8s-{region}-{environment}-{deployment}-{stage}.yaml"
    elif "infra" in targets:
        workflow = f"infra-{region}-{environment}-{deployment}-{stage}.yaml"
    elif "k8s" in targets:
        workflow = f"k8s-{region}-{environment}-{deployment}-{stage}.yaml"

    return workflow


def _trigger_workflow(region, environment, deployment, workflow, branch):
    print(
        f"\n==> triggering workflow: {region}/{environment}/{deployment} ({workflow}) [{branch}]\n"
    )
    with NamedTemporaryFile("w") as file:
        json.dump(_inputs(region, environment, deployment, branch), file)
        file.flush()

        gh.api(
            f"/repos/:owner/:repo/actions/workflows/{workflow}/dispatches",
            "--input",
            file.name,
        )


def _inputs(region, environment, deployment, branch="master"):
    inputs = {
        "ref": branch,
        "inputs": {
            "region": region,
            "environment": environment,
            "deployment": deployment,
        },
    }
    return inputs


def _parse_args():
    parser = argparse.ArgumentParser(description="Github workflow trigger")
    parser.add_argument("-r", "--region", action="store", required=True)
    parser.add_argument("-e", "--environment", action="store", required=True)
    parser.add_argument("-d", "--deployment", action="store", required=True)
    parser.add_argument("--stage", action="store", required=True)
    parser.add_argument("--targets", action="store", required=True)
    parser.add_argument("--branch", action="store", required=True)
    return parser.parse_args()


if __name__ == "__main__":
    main()
