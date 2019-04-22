from __future__ import unicode_literals

import tomlkit
from pathlib2 import Path


def extract(source_file):
    d = Path(source_file)
    result = None
    while d.parent != d and result is None:
        d = d.parent
        pyproject_toml_path = d / "pyproject.toml"
        if pyproject_toml_path.exists():
            pyproject_toml = tomlkit.parse(string=pyproject_toml_path.read_text())
            if "tool" in pyproject_toml and "poetry" in pyproject_toml["tool"]:
                # noinspection PyUnresolvedReferences
                result = pyproject_toml["tool"]["poetry"]["version"]
    return result
