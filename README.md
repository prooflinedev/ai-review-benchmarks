# AI Review Benchmarks

This is a Proofline software engineering challenge. We give you a small application and eight proposed changes. **Your job is to build a benchmark in your fork of this repository, run real AI code reviewers on those changes, and show what you learned.** We’d like to see the code you wrote, the reviews the tools actually produced, and the evidence behind your conclusions.

At Proofline, we care whether a review helps an engineer make a decision before shipping a change. A reviewer can write ten comments and miss the one thing that would break. It can also flag a risk that matters in one deployment and has no effect in another. How would you design an experiment that can tell the difference? This is an especially good project for software engineering intern candidates who enjoy building developer tools. You’ll find the internship, our founding engineering role, and application instructions on the [Proofline careers page](https://proofline.sh/careers/).

## Start with the application

GitHub disables the Fork button for private repositories in our organization. To create your working copy, use **Use this template → Create a new repository**, select **Private**, and copy the default branch. That gives you the application and all eight cases. Do your benchmark development there.

The application schedules reports, delivers them from a queue, and exports their history. It uses Python 3.10+ and SQLite 3.35+ with no extra packages. From the repository root, you can follow one delivery from the queue to a receipt.

```sh
python3 console.py schedule 'Weekly orders' 1700000000
python3 console.py work --queue reports --now 1700000001
python3 console.py summary
```

On a fresh database, the summary should show one delivered report and zero pending. Each review case is a separate change to this same application. Three cases also include records from two simulated deployments, so you can test how a reviewer uses that information. [Application guide](docs/report-service.md) · [Review cases](cases/README.md)

## Build and run your benchmark

1. **Decide what a good review would catch.** Before reading provider output, inspect the changes and write down how you’ll judge a finding. How will you verify that a warning is correct? What will you do if two comments describe the same problem, or a reviewer finds something you missed?
2. **Build a repeatable way to run the comparison.** Choose at least two PR review providers with free credits or trials. Sign up, install them on repositories you control, and give them the same changes and context. Keep your expected answers and the other provider’s comments out of view. Choose the language and tools you’d want to maintain.
3. **Run the reviewers and keep the receipts.** Save the actual review text or links, the commits reviewed, and the settings that affected the run. Use the free allowance. If it runs out, show which cases each provider attempted and compare them on the overlap. A timeout and a completed review with no findings are different outcomes.
4. **Explain one result in detail.** Pick a comment that influenced your assessment. Show the change, quote the reviewer, and explain how you checked its claim. Include the overall results and what this small sample leaves uncertain. Proofline can be one of the reviewers, and it gets the same grading rules as every other provider.

## Share your work

Open a pull request **in your own private repository** with the benchmark implementation, instructions for rerunning it, and a short report linked to the review evidence. Give the Proofline hiring team read access to the PR and any private evidence it references, then share the PR link through the application route for your role. We want to be able to pick a row in your results, trace it back to a real review, and understand why you scored it that way. [Proofline careers](https://proofline.sh/careers/)
