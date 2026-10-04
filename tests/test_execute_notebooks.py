"""Test normalizing the log messages in the outputs of an executed notebook.

The committed outputs should change only when the code does. A detail of one run which slipped
through would make every run look like a change.
"""

# pylint: disable=missing-function-docstring

import execute_notebooks


def test_drops_time_thread_and_task() -> None:
    text = "[ 2026-09-29 14:44:31.070: T3: K17: Debug: Metacells: Blocks: 12\n"
    assert execute_notebooks.normalized_log(text) == "[ Debug: Metacells: Blocks: 12\n"


def test_drops_process() -> None:
    text = "[ 2026-09-29 14:44:31.070: P2: T1: K1: Info: Main: done\n"
    assert execute_notebooks.normalized_log(text) == "[ Info: Main: done\n"


def test_drops_time_of_a_single_thread() -> None:
    text = "[ 2026-09-29 14:44:31.070: Debug: Main: hello\n"
    assert execute_notebooks.normalized_log(text) == "[ Debug: Main: hello\n"


def test_normalizes_the_first_line_of_a_long_message() -> None:
    text = "┌ 2026-09-29 14:44:31.070: T2: K5: Debug: Main: first\n│ second\n└ third\n"
    assert execute_notebooks.normalized_log(text) == "┌ Debug: Main: first\n│ second\n└ third\n"


def test_normalizes_every_message() -> None:
    text = (
        "[ 2026-09-29 14:44:31.070: T1: K1: Debug: Main: a\n"
        "plain\n"
        "[ 2026-09-29 14:44:32.000: T2: K9: Debug: Main: b\n"
    )
    assert execute_notebooks.normalized_log(text) == "[ Debug: Main: a\nplain\n[ Debug: Main: b\n"


def test_leaves_other_output_alone() -> None:
    text = "metacells.I0.R0: 0.5\n[ not a log message: T1: K1:\n"
    assert execute_notebooks.normalized_log(text) == text
