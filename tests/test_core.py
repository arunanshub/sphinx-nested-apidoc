from __future__ import annotations

import os

from hypothesis import given
from hypothesis_fspaths import fspaths
from pytest_mock import MockerFixture

from sphinx_nested_apidoc import core

from . import dotted_filenames


@given(path=fspaths())
def test_sanitize_path(path: str):
    sanitized_path = core.sanitize_path(os.fsdecode(path))
    assert not os.path.isabs(sanitized_path)


@given(dotted_filenames())
def test_get_nested_dir_filename(filename: str):
    nested = core.get_nested_dir_filename(filename)
    path, ext = os.path.splitext(nested)
    # the only `.` in nested path is the extension separator.
    assert not path.count(".")
    # the extensions of filename and nested path should match.
    assert os.path.splitext(filename)[-1] == ext


class TestFeedSphinxApidocFunc:
    def test_help_in_argument(self, mocker: MockerFixture):
        apidoc_main = mocker.patch("sphinx_nested_apidoc.core.apidoc.main")

        output_dir = "output"
        module_path = "module"

        for arg in "-h", "--help":
            core.feed_sphinx_apidoc(output_dir, module_path, arg)
            apidoc_main.assert_called_with(
                [
                    "--output-dir",
                    output_dir,
                    module_path,
                    "--separate",
                    "--suffix",
                    "rst",
                    arg,
                ]
            )

    def test_implicit_namespaces_argument(self, mocker: MockerFixture):
        apidoc_main = mocker.patch("sphinx_nested_apidoc.core.apidoc.main")

        output_dir = "output"
        module_path = "module"

        core.feed_sphinx_apidoc(
            output_dir,
            module_path,
            implicit_namespaces=True,
        )
        apidoc_main.assert_called_once_with(
            [
                "--output-dir",
                output_dir,
                module_path,
                "--separate",
                "--suffix",
                "rst",
                "--implicit-namespaces",
            ]
        )

    def test_force_argument(self, mocker: MockerFixture):
        apidoc_main = mocker.patch("sphinx_nested_apidoc.core.apidoc.main")

        output_dir = "output"
        module_path = "module"

        core.feed_sphinx_apidoc(
            output_dir,
            module_path,
            force=True,
        )
        apidoc_main.assert_called_with(
            [
                "--output-dir",
                output_dir,
                module_path,
                "--separate",
                "--suffix",
                "rst",
                "--force",
            ]
        )

    def test_dry_run_flag_removed(self, mocker: MockerFixture):
        apidoc_main = mocker.patch("sphinx_nested_apidoc.core.apidoc.main")

        output_dir = "output"
        module_path = "module"

        for arg in "-n", "--dry-run":
            core.feed_sphinx_apidoc(output_dir, module_path, arg)
            apidoc_main.assert_called_with(
                [
                    "--output-dir",
                    output_dir,
                    module_path,
                    "--separate",
                    "--suffix",
                    "rst",
                ]
            )

    # TODO: check working of _add_flag_if_not_present
