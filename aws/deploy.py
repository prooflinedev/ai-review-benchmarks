"""Package, deploy and invoke the benchmark workload. Requires Git and AWS CLI v2."""

import argparse
import json
from pathlib import Path
import re
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
OWNER_TAG = {"Key": "Application", "Value": "ai-review-benchmarks"}
REQUEST = {"report": "Weekly orders", "scheduled_at": 100, "queue": "reports", "run_at": 101}


def git(*args):
    return subprocess.check_output(["git", "-C", str(ROOT), *args], text=True)


def revision():
    return git("rev-parse", "--verify", "HEAD^{commit}").strip()


def package(commit):
    def source(path):
        return git("show", f"{commit}:{path}")

    migrations = git("ls-tree", "-r", "--name-only", commit, "migrations/").splitlines()
    files = {path: source(path) for path in ["reports.py", *migrations]}
    # CloudFormation packages inline Python as index.py. Materialize the original
    # app layout once per cold start so reports.migrate() can find its SQL files.
    loader = f"""import sys
import tempfile
from pathlib import Path

SOURCE_COMMIT = {commit!r}
app = Path(tempfile.mkdtemp())
for name, body in {files!r}.items():
    dest = app / name
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(body, encoding="utf-8")
sys.path.insert(0, str(app))

"""
    template = json.loads(source("aws/stack.json"))
    template["Resources"]["ReportFunction"]["Properties"]["Code"]["ZipFile"] = loader + source("aws/handler.py")
    body = json.dumps(template, indent=2) + "\n"
    if len(body.encode()) > 51200:
        raise ValueError("The fixture exceeds CloudFormation's 51,200-byte inline template limit.")
    return body


def verify_response(response, commit):
    expected = {"commit": commit, "report": REQUEST["report"], "delivered_this_run": 1,
                "receipt_at": REQUEST["run_at"], "summary": {"delivered": 1, "pending": 0}}
    if not response.get("request_id") or any(response.get(k) != v for k, v in expected.items()):
        raise ValueError(f"Deployment verification failed for {commit}: {response}")
    print(json.dumps(response, indent=2))


def smoke(path, commit):
    template = json.loads(path.read_text())
    code = template["Resources"]["ReportFunction"]["Properties"]["Code"]["ZipFile"]
    with tempfile.TemporaryDirectory() as tmp:
        entry = Path(tmp) / "index.py"
        entry.write_text(code)
        # A fresh interpreter reproduces Lambda's cold import with no application
        # checkout on sys.path. All extracted files go into the disposable directory.
        driver = """
import json
import runpy
import sys
import tempfile
from types import SimpleNamespace

tempfile.tempdir, entry, payload = sys.argv[1:]
handler = runpy.run_path(entry)["handler"]
response = handler(json.loads(payload), SimpleNamespace(aws_request_id="local-smoke"))
print(json.dumps(response))
"""
        child = subprocess.run(
            [sys.executable, "-I", "-c", driver, tmp, str(entry), json.dumps(REQUEST)],
            check=True, text=True, stdout=subprocess.PIPE,
        )
        verify_response(json.loads(child.stdout), commit)


def aws(region, *args):
    result = subprocess.run(
        ["aws", "--no-cli-pager", "--region", region, "--output", "json", *args],
        check=True, capture_output=True, text=True,
    )
    return json.loads(result.stdout) if result.stdout.strip() else None


def existing_stack(args):
    try:
        stack = aws(args.region, "cloudformation", "describe-stacks", "--stack-name", args.stack)["Stacks"][0]
    except subprocess.CalledProcessError as error:
        if "(ValidationError)" in error.stderr and f"Stack with id {args.stack} does not exist" in error.stderr:
            return None
        raise
    if OWNER_TAG not in stack.get("Tags", []):
        raise ValueError(f"Stack {args.stack} already exists without the challenge's Application tag.")
    return stack


def deploy(args, commit):
    stack = existing_stack(args)
    operation = "update" if stack else "create"
    with tempfile.TemporaryDirectory() as tmp:
        artifact = Path(tmp) / "stack.json"
        artifact.write_text(package(commit))
        try:
            aws(args.region, "cloudformation", f"{operation}-stack", "--stack-name", args.stack,
                "--template-body", f"file://{artifact}",
                "--parameters", f"ParameterKey=RuntimeRole,ParameterValue={args.role_arn}",
                "--tags", json.dumps([OWNER_TAG]), *([] if stack else ["--on-failure", "DELETE"]))
        except subprocess.CalledProcessError as error:
            if operation == "update" and "No updates are to be performed" in error.stderr:
                print(f"{args.stack} already has this template.")
                return
            raise
    aws(args.region, "cloudformation", "wait", f"stack-{operation}-complete", "--stack-name", args.stack)
    print(f"Deployed {commit} to {args.stack} in {args.region}.")


def verify(args, commit):
    with tempfile.TemporaryDirectory() as tmp:
        response = Path(tmp) / "response.json"
        invocation = aws(args.region, "lambda", "invoke", "--function-name", args.stack,
                         "--cli-binary-format", "raw-in-base64-out", "--payload", json.dumps(REQUEST),
                         str(response))
        if invocation.get("StatusCode") != 200 or invocation.get("FunctionError"):
            raise ValueError(f"Lambda invocation failed: {invocation} {response.read_text()}")
        verify_response(json.loads(response.read_text()), commit)


def delete(args):
    stack = existing_stack(args)
    if stack is None:
        print(f"{args.stack} is absent in {args.region}.")
        return
    stack_id = stack["StackId"]
    aws(args.region, "cloudformation", "delete-stack", "--stack-name", stack_id)
    aws(args.region, "cloudformation", "wait", "stack-delete-complete", "--stack-name", stack_id)
    print(f"Removed {args.stack} from {args.region}.")


def main():
    cli = argparse.ArgumentParser(description=__doc__)
    commands = cli.add_subparsers(dest="operation", required=True)
    commands.add_parser("package").add_argument("--output", type=Path, required=True)
    commands.add_parser("smoke").add_argument("--template", type=Path, required=True)
    for operation in ("deploy", "verify", "delete"):
        sub = commands.add_parser(operation)
        sub.add_argument("--stack", default="ai-review-bench")
        sub.add_argument("--region", required=True)
        if operation == "deploy":
            sub.add_argument("--role-arn", required=True)
    args = cli.parse_args()
    if hasattr(args, "stack") and not re.fullmatch(r"[A-Za-z][A-Za-z0-9-]{0,63}", args.stack):
        cli.error("Choose a stack name of up to 64 letters, digits and hyphens starting with a letter.")
    if args.operation == "delete":
        delete(args)
        return
    commit = revision()
    if args.operation == "package":
        args.output.write_text(package(commit))
    elif args.operation == "smoke":
        smoke(args.template, commit)
    elif args.operation == "deploy":
        deploy(args, commit)
    else:
        verify(args, commit)


if __name__ == "__main__":
    try:
        main()
    except subprocess.CalledProcessError as error:
        sys.exit(error.stderr or str(error))
    except (ValueError, OSError) as error:
        sys.exit(str(error))
