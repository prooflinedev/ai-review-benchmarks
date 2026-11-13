# Deploy from GitHub Actions

Use a private copy of the starter in your own GitHub account and an AWS account you control. The PR workflow packages the checked-out app and runs a report through the packaged Lambda handler. It runs without AWS credentials. The deployment workflow runs on request from `main`, exchanges a GitHub OIDC token for temporary credentials, deploys the sample in one AWS Region, and invokes it. Save the workflow URL, revision, and verified response for your report.

## One-time setup in your account

1. Enable Actions in your private repository. Pick an AWS Region that supports Lambda and check your free allowances. Run the commands below from that checkout, with GitHub CLI signed in and AWS CLI v2 signed in as an account administrator or identity allowed to provision the two roles.
2. In AWS IAM → Identity providers, select the existing GitHub OpenID Connect provider or add one with URL `https://token.actions.githubusercontent.com` and audience `sts.amazonaws.com`. This is an account-wide identity provider that other projects may also use. [GitHub’s AWS OIDC setup](https://docs.github.com/en/actions/how-tos/secure-your-work/security-harden-deployments/oidc-in-aws)
3. Set the trust condition to the **exact subject for your copy’s main branch**. For a new repository using GitHub’s immutable subject format, these commands derive it from the repository and owner IDs. Older repositories using name-only subjects use `repo:OWNER/REPOSITORY:ref:refs/heads/main`. If you’ve customized the subject, inspect your repository’s OIDC settings first. [GitHub subject formats](https://docs.github.com/en/actions/reference/security/oidc#immutable-subject-claims)

```sh
export AWS_REGION=us-east-1
repo=$(gh repo view --json nameWithOwner --jq .nameWithOwner)
subject=$(gh api "repos/$repo" --jq '"repo:\(.owner.login)@\(.owner.id)/\(.name)@\(.id):ref:refs/heads/main"')
aws sts get-caller-identity
aws cloudformation deploy --region "$AWS_REGION" \
  --stack-name ai-review-bench-github --template-file aws/github-roles.yaml \
  --capabilities CAPABILITY_IAM --parameter-overrides GitHubSubject="$subject"
```

The bootstrap stack creates two roles. The workflow role can manage the named sample stack, Lambda function and log group, and pass the runtime role to Lambda. The runtime role can write streams in that log group. The deploy workflow uses these repository **variables**. No AWS access key is stored in GitHub.

```sh
stack_output() {
  aws cloudformation describe-stacks --region "$AWS_REGION" --stack-name ai-review-bench-github \
    --query "Stacks[0].Outputs[?OutputKey=='$1'].OutputValue | [0]" --output text
}
gh variable set AWS_REGION --repo "$repo" --body "$AWS_REGION"
gh variable set AWS_DEPLOY_ROLE_ARN --repo "$repo" --body "$(stack_output DeploymentRoleArn)"
gh variable set AWS_LAMBDA_ROLE_ARN --repo "$repo" --body "$(stack_output RuntimeRoleArn)"
```

## Deploy, verify, and remove

In **Actions → AWS sample deployment → Run workflow**, choose `main` and `deploy`. Check the commit on the workflow run and the response in **Deploy and verify one report**. Save the evidence while the stack is available. The same operation can be run from the command line.

```sh
gh workflow run aws.yml --repo "$repo" --ref main -f operation=deploy
```

When you finish, dispatch the workflow again with `delete`. Wait for **Delete the sample deployment** to finish before removing the roles. If the deploy or verify step fails, inspect the failed operation and follow the cleanup instructions in the [AWS deployment guide](aws.md).

```sh
gh workflow run aws.yml --repo "$repo" --ref main -f operation=delete
# After the delete workflow succeeds, remove the roles from your AWS account.
aws cloudformation delete-stack --region "$AWS_REGION" --stack-name ai-review-bench-github
aws cloudformation wait stack-delete-complete --region "$AWS_REGION" --stack-name ai-review-bench-github
```

If you created the OIDC provider exclusively for this experiment, you can remove it after both stacks are gone. Keep shared providers in place.
