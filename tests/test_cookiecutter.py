"""UT-AC-9: the component cookiecutter renders every file for every component kind"""
import re
from pathlib import Path

import pytest
from cookiecutter.main import cookiecutter

TEMPLATE = Path(__file__).resolve().parents[1] / "cookiecutters" / "component"


@pytest.mark.parametrize("kind", ["active", "passive", "queued"])
def test_ut_ac_9_renders_each_kind(tmp_path, kind):
    cookiecutter(str(TEMPLATE), no_input=True, output_dir=str(tmp_path),
                 extra_context={"component_name": "Widget", "component_namespace": "Demo", "component_kind": kind})
    out = tmp_path / "Widget"
    for rendered in ("Widget.fpp", "Widget.rs", "CMakeLists.txt", "docs/sdd.md"):
        assert (out / rendered).is_file(), rendered
    fpp = (out / "Widget.fpp").read_text()
    assert "@ fprime-rust" in fpp and f"{kind} component Widget" in fpp
    assert bool(re.search(r"\bsync command HELLO", fpp)) == (kind == "passive")
    rs = (out / "Widget.rs").read_text()
    assert "use crate::widget_base::*;" in rs and "impl Component for Widget" in rs
    assert ("NOTE (queued component)" in rs) == (kind == "queued")
    assert ("sync input port run: Svc.Sched" in fpp) == (kind == "queued")
    assert 'Widget.rs"' in (out / "CMakeLists.txt").read_text()


def test_ut_ac_9_rejects_bad_name(tmp_path):
    from cookiecutter.exceptions import FailedHookException
    with pytest.raises(FailedHookException):
        cookiecutter(str(TEMPLATE), no_input=True, output_dir=str(tmp_path),
                     extra_context={"component_name": "bad name", "component_kind": "passive"})
