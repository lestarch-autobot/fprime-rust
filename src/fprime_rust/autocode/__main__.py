"""fprime_rust.autocode.__main__: the ``fprime-rust-ac`` command

``bindings``: generate the C++ shim, Rust base module and template of every ``@ fprime-rust`` component in a
module's translation units (model from ``fpp-cache/stdout.txt``). ``crate``: emit the deployment workspace.
Both accept ``--dry-run`` to list the files that would be written, one per line, without writing.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Dict, List

from . import cpp_shim, rust_base, rust_template
from .crate import CrateMember, workspace_files, write_if_changed
from .model import ModelError, load_module_model
from .view import ModelView, UnsupportedElement


def bindings_files(build_dir: Path, output: Path, prefixes: List[Path], units: List[Path]) -> Dict[Path, str]:
    """Generated files of a module as {path: content}; the user template seed is included only when absent"""
    model = load_module_model(build_dir, units)
    model_name = ", ".join(unit.name for unit in units)
    files: Dict[Path, str] = {}
    for view in ModelView(model, prefixes).views():
        template = rust_template.generate(view)
        files[output / f"{view.name}.hpp"] = cpp_shim.generate_hpp(view, model_name)
        files[output / f"{view.name}.cpp"] = cpp_shim.generate_cpp(view, model_name)
        files[output / f"{view.base_module}.rs"] = rust_base.generate(view, model_name)
        files[output / f"{view.name}.template.rs"] = template
        seed = user_file_for(view.name, units)
        if seed is not None and not seed.exists():
            files[seed] = template
    return files


def component_specs(build_dir: Path, output: Path, prefixes: List[Path], units: List[Path]) -> List[str]:
    """``Ns.Comp=<base.rs>=<Comp.rs>`` of every Rust component in the module, for the ``crate`` subcommand"""
    model = load_module_model(build_dir, units)
    return [f"{view.qualified_name}={output / (view.base_module + '.rs')}={user_file_for(view.name, units)}"
            for view in ModelView(model, prefixes).views()]


def user_file_for(component_name: str, units: List[Path]) -> Path:
    """Where the user's ``<Comp>.rs`` lives: next to the translation unit defining the component"""
    for unit in units:
        if unit.stem == component_name:
            return unit.with_name(f"{component_name}.rs")
    return units[0].with_name(f"{component_name}.rs") if units else None


def parse_member(spec: str) -> CrateMember:
    """``Ns.Comp=<base.rs>=<User.rs>``"""
    try:
        qualified, base, user = spec.split("=", 2)
    except ValueError:
        raise argparse.ArgumentTypeError(f"--component expects Ns.Comp=<base.rs>=<Comp.rs>, got {spec!r}") from None
    return CrateMember(qualified, Path(base), Path(user))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="fprime-rust-ac", description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)
    bindings = sub.add_parser("bindings", help="generate the per-module shim, base module and template")
    bindings.add_argument("build_dir", type=Path, help="module build directory containing fpp-cache/stdout.txt")
    bindings.add_argument("--output-directory", type=Path, required=True)
    bindings.add_argument("--prefixes", type=Path, nargs="+", required=True, help="FPRIME_BUILD_LOCATIONS")
    bindings.add_argument("--translation-units", type=Path, nargs="+", required=True)
    bindings.add_argument("--dry-run", action="store_true")
    components = sub.add_parser("components", help="list the module's Rust components as Ns.Comp=<base.rs>=<Comp.rs>")
    components.add_argument("build_dir", type=Path)
    components.add_argument("--output-directory", type=Path, required=True)
    components.add_argument("--prefixes", type=Path, nargs="+", required=True)
    components.add_argument("--translation-units", type=Path, nargs="+", required=True)
    crate = sub.add_parser("crate", help="emit the deployment-level Cargo workspace")
    crate.add_argument("--output-directory", type=Path, required=True)
    crate.add_argument("--target", required=True, help="executable name; the archive is libfprime_rust_<target>.a")
    crate.add_argument("--runtime", type=Path, required=True, help="path of the fprime-rust runtime crate")
    crate.add_argument("--component", type=parse_member, action="append", default=[], help="Ns.Comp=<base.rs>=<Comp.rs>")
    crate.add_argument("--dry-run", action="store_true")
    return parser


def emit(files: Dict[Path, str], dry_run: bool) -> None:
    for path in sorted(files):
        if dry_run:
            print(path)
        else:
            write_if_changed(path, files[path])


def main(argv: List[str] = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        if args.command == "bindings":
            files = bindings_files(args.build_dir, args.output_directory, args.prefixes, args.translation_units)
        elif args.command == "components":
            for spec in component_specs(args.build_dir, args.output_directory, args.prefixes, args.translation_units):
                print(spec)
            return 0
        else:
            files = workspace_files(args.output_directory, args.target, args.runtime, args.component)
    except (ModelError, UnsupportedElement) as error:
        print(f"[ERROR] fprime-rust-ac: {error}", file=sys.stderr)
        return 1
    emit(files, args.dry_run)
    return 0


if __name__ == "__main__":
    sys.exit(main())
