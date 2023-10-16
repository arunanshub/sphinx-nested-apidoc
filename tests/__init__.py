from __future__ import annotations

import os
from dataclasses import dataclass

from hypothesis import HealthCheck, settings
from hypothesis import strategies as st
from hypothesis_fspaths import fspaths


@dataclass
class PathLike(os.PathLike):
    path: str

    def __fspath__(self):
        return self.path


@st.composite
def generate_path(
    draw: st.DrawFn,
    maxdepth: int = 15,
    extension: bool = True,
    absolute: bool = True,
    allow_pathlike: bool = True,
) -> str | os.PathLike:
    # Define a strategy for generating valid characters for path names
    valid_chars = st.characters(
        whitelist_categories=("L", "N", "P"),
        blacklist_characters=r'\/.<>:"|?*',
    )

    # Define a strategy for generating valid drive letters for Windows
    drive_strategy = st.sampled_from("ABCDEFGHIJKLMNOPQRSTUVWXYZ").map(
        lambda d: f"{d}:"
    )

    # Define a strategy for generating valid separators (forward or backward slash)
    separator_strategy = st.sampled_from(["/", "\\"])

    # Define a strategy for generating valid file extensions
    extension_strategy = st.text(valid_chars, min_size=1, max_size=4).map(
        lambda e: f".{e}"
    )

    # Define a strategy for generating valid path names
    path_strategy = (
        st.lists(
            st.text(valid_chars, min_size=1),
            min_size=1,
            max_size=maxdepth,
        )
        .flatmap(
            lambda components: st.tuples(
                st.just(components),
                st.lists(
                    separator_strategy,
                    min_size=len(components) - 1,
                    max_size=len(components) - 1,
                ),
            )
        )
        .map(lambda x: "".join(sum(zip(x[0], x[1] + [""]), ())))
    )

    # Generate a valid drive letter for Windows (optional)
    drive = draw(st.one_of(st.none(), drive_strategy)) if absolute else None

    # Generate a valid path name using the strategy
    path = draw(path_strategy)

    # Generate a valid file extension (optional)
    ext = draw(extension_strategy) if extension else ""

    # Combine the drive letter, path name, and file extension (if applicable)
    if drive is not None:
        path = f"{drive}/{path}{ext}"
    else:
        path = f"{path}{ext}"

    # Convert the path to an os.PathLike object (optional)
    if allow_pathlike:
        pathlike_strategy = st.sampled_from([str, PathLike])
        pathlike_func = draw(pathlike_strategy)
        path = pathlike_func(path)

    return path


@settings(suppress_health_check=[HealthCheck.too_slow])
@st.composite
def dotted_filenames(draw: st.DrawFn, maxdepth: int = 15) -> str:
    """Generates sphinx-apidoc like filenames.

    Args:
        draw: A :py:class:`draw.DrawFn` object.
        maxdepth: The maximum depth of the directory tree.

    Returns:
        A randomly generated file path.
    """
    # folder that contains the sphinx-apidoc file
    folder_name = os.fsdecode(draw(generate_path(maxdepth)))
    # build a sphinx-apidoc equivalent filename
    text_st = st.text(
        st.characters(blacklist_characters=[".", "/", "\\"]),
        min_size=1,
    )
    filename = draw(text_st)
    for _ in range(maxdepth):
        filename += f".{draw(text_st)}"
    full_path = os.path.join(folder_name, filename)
    # add extension to file
    extension = draw(text_st | st.none())
    full_path = (
        f"{full_path}{os.path.extsep}{extension}"
        if extension is not None
        else full_path
    )
    return full_path
