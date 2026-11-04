# task_graph

Draws `docs/task_graph.png`: one box per task, colored by language, with an arrow from each task to the tasks
that read its outputs. Dashed boxes are tasks outside the default build. Not part of the default build: run
`pixi run task-graph`.

- **Inputs:** every task's `SConscript` and `paper/generated_manifest.csv`.
