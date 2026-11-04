# Demo Julia task: production function by OLS, with the standard library only.
# Runs through SCons or on its own, from any working directory (see helpers/README.md).
include(joinpath(@__DIR__, "..", "..", "..", "helpers", "project_paths.jl"))
paths = project_paths(@__DIR__)

using DelimitedFiles

data, header = readdlm(joinpath(paths.task_output_root, "01_example_clean", "panel.csv"), ',', header=true)
column(name) = Float64.(data[:, findfirst(==(name), vec(header))])

X = hcat(ones(size(data, 1)), column("log_capital"), column("log_labor"))
beta = X \ column("log_output")
terms = ["const", "log_capital", "log_labor"]
foreach(((t, b),) -> println(t, " = ", round(b, digits=3)), zip(terms, beta))

writedlm(joinpath(paths.task_output_dir, "coefficients.csv"), vcat(["term" "estimate"], hcat(terms, beta)), ',')
