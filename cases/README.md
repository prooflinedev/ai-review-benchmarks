# Review cases

Each directory contains a proposed PR title, description, and patch against the same application baseline. Cases 04, 05, and 06 also contain an optional deployment snapshot. If you supply a snapshot to a reviewer, give its comparison partner the same snapshot and record that choice.

| Case | Proposed change | Reference PR |
| --- | --- | --- |
| 01 | Page report history by scheduled time | [View diff](https://github.com/prooflinedev/ai-review-benchmarks/pull/1/files) |
| 02 | Stream the report export | [View diff](https://github.com/prooflinedev/ai-review-benchmarks/pull/2/files) |
| 03 | Batch queued deliveries | [View diff](https://github.com/prooflinedev/ai-review-benchmarks/pull/3/files) |
| 04 | Retire the legacy delivery column | [View diff](https://github.com/prooflinedev/ai-review-benchmarks/pull/4/files) |
| 05 | Increase export batch size | [View diff](https://github.com/prooflinedev/ai-review-benchmarks/pull/5/files) |
| 06 | Use the new delivery queue | [View diff](https://github.com/prooflinedev/ai-review-benchmarks/pull/6/files) |
| 07 | Index pending deliveries | [View diff](https://github.com/prooflinedev/ai-review-benchmarks/pull/7/files) |
| 08 | Include a total in the activity summary | [View diff](https://github.com/prooflinedev/ai-review-benchmarks/pull/8/files) |

To inspect the first change in a fresh copy of the starter, run the commands below from the repository root. Apply each patch to its own branch starting at the same baseline.

```sh
git switch -c inspect-history
git apply -p0 cases/01/change.patch
git diff
```

If you want a reviewer to see only the application, the upstream branch `pilot/base` contains just its source and usage guide. The branches `pilot/01` through `pilot/08` each add one change to that base. You can fetch these refs from the starter and push the same commits into separate private run repositories. Keep the benchmark implementation and your report in your own copy of the starter.
