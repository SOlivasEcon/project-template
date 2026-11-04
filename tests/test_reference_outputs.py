"""Regression test: each output listed in reference_outputs.json still has its recorded hash (see reference.py).

Needs a finished build. When a result changes on purpose (new data, a method change), check the new output,
then record it again with `python tests/reference.py <task>/<file>`.
"""

import pytest

from reference import digest, load

REFERENCE = load()


@pytest.mark.parametrize("relative_path", sorted(REFERENCE))
def test_output_matches_reference(relative_path):
    from project_package.config import TASK_OUTPUT_ROOT

    path = TASK_OUTPUT_ROOT / relative_path
    assert path.is_file(), f"{relative_path} not built; run the build first (`pixi run build`)"
    assert digest(path) == REFERENCE[relative_path], (
        f"{relative_path} differs from its reference; if the change is intended, record it again "
        f"with `python tests/reference.py {relative_path}`"
    )
