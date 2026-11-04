# Demo Julia task: production function by OLS, with the standard library only.
# Run it through SCons (`python -m SCons example_julia`), which sets TASK_OUTPUT_ROOT and TASK_OUTPUT_DIR.

using DelimitedFiles

upstream = get(ENV, "TASK_OUTPUT_ROOT", "")
out = get(ENV, "TASK_OUTPUT_DIR", "")
if isempty(upstream) || isempty(out)
    error("TASK_OUTPUT_ROOT / TASK_OUTPUT_DIR not set: run this script through SCons.")
end

data, header = readdlm(joinpath(upstream, "01_example_clean", "panel.csv"), ',', header=true)
column(name) = Float64.(data[:, findfirst(==(name), vec(header))])

X = hcat(ones(size(data, 1)), column("log_capital"), column("log_labor"))
beta = X \ column("log_output")
terms = ["const", "log_capital", "log_labor"]
foreach(((t, b),) -> println(t, " = ", round(b, digits=3)), zip(terms, beta))

writedlm(joinpath(out, "coefficients.csv"), vcat(["term" "estimate"], hcat(terms, beta)), ',')
