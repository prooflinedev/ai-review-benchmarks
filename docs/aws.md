# Deploy and verify the report workload on AWS

The starter deploys the report service as one private, on-demand Lambda function. A request schedules a report, runs its queue worker, and returns the delivery receipt, summary, Git commit and Lambda request ID. Every invocation applies the application's SQL migrations to a fresh SQLite database held in memory. Keep a copy of the response if you want evidence after the request finishes.

The stack owns the function and its CloudWatch log group. Logs expire after one day. Only an authenticated caller with invocation permission can run the function. A deployment gives you a real AWS observation to cite separately from the simulated inventories in the review cases.

## Package a revision

Commit the source you want to deploy. The packager reads the handler, application, migrations and CloudFormation definition from the exact Git commit checked out. It embeds them in an inline Lambda package. Building it requires Python 3.10+ and Git. Running the SQLite smoke check requires SQLite 3.35+.

```sh
python3 aws/deploy.py package --output /tmp/review-bench-stack.json
python3 aws/deploy.py smoke --template /tmp/review-bench-stack.json
```

The smoke command checks that the packaged code can create a receipt for one due report and return the correct commit. The local smoke response carries the request ID `local-smoke`. An AWS invocation supplies its own request ID. Keep those results distinct.

## Deploy in your AWS account

Use AWS CLI v2 with short-lived credentials. In your own account, set up the execution and deployment roles once. The execution role trusts the Lambda service and can write to this function’s log group. The deployer can pass that specific role to Lambda. Use GitHub OIDC for deployment from your repository. [GitHub Actions and AWS roles](github-aws.md)

Choose one region and use the stack name configured in your IAM policy. The commands below assume `AWS_REGION` and `AWS_LAMBDA_ROLE_ARN` are set in the shell, and the permitted stack name is `ai-review-bench`.

```sh
aws sts get-caller-identity
python3 aws/deploy.py deploy --region "$AWS_REGION" --stack ai-review-bench --role-arn "$AWS_LAMBDA_ROLE_ARN"
python3 aws/deploy.py verify --region "$AWS_REGION" --stack ai-review-bench
```

`deploy` creates or updates the stack and waits for CloudFormation. Repeating it for the same commit and role accepts an unchanged stack. `verify` invokes the deployed function and checks the returned commit, report name, worker count, receipt timestamp and final counts. The expected summary for the starter is one delivered and zero pending. If the observed behavior changes, keep that result and investigate the reviewed revision. For candidate-specific scenarios, design additional probes and record their input and output.

If a deployment fails, inspect **CloudFormation → Stacks → Events** in the same region. A failed first creation requests automatic deletion. A failed update normally rolls back. Use the cleanup command after stack operations finish, including after a failed smoke check.

## Cost and cleanup

AWS offers signup credits to eligible new customers. Check the credit balance, plan type, expiry and available services in your own Billing console. This example uses a 128 MB Lambda with a ten-second timeout, direct invocation, and one short-lived log group. There are no timers or provisioned workers. Function requests, execution time and logs are metered. Covered pilot usage can cost $0 out of pocket. [AWS Free Tier](https://aws.amazon.com/free/) · [Lambda pricing](https://aws.amazon.com/lambda/pricing/) · [CloudWatch pricing](https://aws.amazon.com/cloudwatch/pricing/)

```sh
python3 aws/deploy.py delete --region "$AWS_REGION" --stack ai-review-bench
```

Deletion waits for the function and log group to be removed. Running it again confirms the stack is absent. Remove the separate roles stack when you finish using GitHub deployment, as described in the [setup guide](github-aws.md).
