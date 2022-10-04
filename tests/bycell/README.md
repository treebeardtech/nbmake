# Nbmake "By Cell" Mode

With the `--nbmake-by-cell` flag, nbmake will carve up the notebook into
multiple individual unit tests. Each section heading (of any level) will be
split out as a separate test, as long as it contains at least one code cell.
Sections without code cells will be ignored. All the cells within a section will
be run consecutively, in order.

The title of each heading will be used as the name of each test.

An optional initial section without a heading serves as a common initialization
block which will be prepended to all tests in the file.

## Example

For example, the following notebook structure would result in two unit tests:

    import re

    # test 1: check asterisk

    assert re.match("a*", "a")
    assert re.match("a*", "aa")
    assert not re.match("a*", "b")

    # comments

    Note that this section happens to be ignored, because it has no codes.

    # test 1: check plus

    assert not re.match("a+", "a")
    assert re.match("a+", "aa")
    assert not re.match("a+", "b")

