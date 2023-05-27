from __future__ import annotations

import os

from hypothesis import strategies as st
from hypothesis_fspaths import fspaths


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
    folder_name = os.fsdecode(draw(fspaths(False)))
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
