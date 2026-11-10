"""fprime_rust.autocode.model:

Loads the FPP model the Rust bindings are generated from.

The model is analyzed in-process by ``fpp.analyze`` (fprime-fpp-python); no JSON model is generated or
read (REQ-FprimeRust-002). The complete set of FPP files is the module's own translation units plus the
transitive closure F Prime's ``fpp-depend`` sub-build leaves in the module build cache at
``fpp-cache/stdout.txt`` (REQ-FprimeRust-003).
"""
from __future__ import annotations

import re
from pathlib import Path
from typing import Iterable, List

import fpp

#: fpp-depend writes the module's transitive FPP closure here, one path per line
IMPORT_LIST_PATH = Path("fpp-cache") / "stdout.txt"


class ModelError(Exception):
    """The FPP model could not be loaded"""


def read_closure(cache_file: Path) -> List[Path]:
    """Read the FPP closure out of the module build cache

    Args:
        cache_file: The ``fpp-cache/stdout.txt`` file of the module
    Returns:
        The paths listed, in order
    Raises:
        ModelError: The file is missing, empty, or lists a path that is not a readable file (REQ-034)
    """
    if not cache_file.is_file():
        raise ModelError(f"FPP closure cache {cache_file} does not exist; has the fpp_depend sub-build run?")
    entries = [
        Path(entry.strip())
        for entry in re.split(r"[;\r\n]+", cache_file.read_text(encoding="utf-8"))
        if entry.strip()
    ]
    if not entries:
        raise ModelError(f"FPP closure cache {cache_file} is empty")
    for entry in entries:
        if not entry.is_file():
            raise ModelError(f"FPP closure cache {cache_file} lists {entry}, which is not a readable file")
    return entries


def deduplicate(paths: Iterable[Path], *, exclude: Iterable[Path] = ()) -> List[Path]:
    """Drop repeated paths keeping the first occurrence, and drop every path in ``exclude``"""
    seen = {path.resolve() for path in exclude}
    unique: List[Path] = []
    for path in paths:
        resolved = path.resolve()
        if resolved in seen:
            continue
        seen.add(resolved)
        unique.append(path)
    return unique


def load_model(sources: Iterable[Path], imports: Iterable[Path]) -> fpp.Model:
    """Analyze the model made of ``sources`` (generated for) and ``imports`` (reference resolution only)

    Raises:
        ModelError: A listed file is missing or the model has diagnostics (REQ-004)
    """
    source_paths = deduplicate(sources)
    import_paths = deduplicate(imports, exclude=source_paths)
    missing = [path for path in source_paths + import_paths if not path.is_file()]
    if missing:
        raise ModelError("FPP files do not exist:\n" + "\n".join(f"  {path}" for path in missing))
    model = fpp.analyze([str(path) for path in source_paths], imports=[str(path) for path in import_paths])
    if model.has_errors:
        raise ModelError(
            f"FPP model has {model.error_count} error(s):\n"
            + "\n".join(f"  {diagnostic.display}" for diagnostic in model.diagnostics)
        )
    return model


def load_module_model(build_directory: Path, translation_units: Iterable[Path]) -> fpp.Model:
    """Load the model of a module from its build directory's closure cache and its translation units"""
    closure = read_closure(build_directory / IMPORT_LIST_PATH)
    return load_model(list(translation_units), closure)
