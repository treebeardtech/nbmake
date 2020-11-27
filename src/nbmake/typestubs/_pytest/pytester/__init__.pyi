from typing import Any


class Testdir:
    tmpdir: str

    def inline_genitems(self, *args: Any) -> Any:
        ...

    def inline_run(self, *args: Any) -> Any:
        ...

    def mkdir(self, path: str) -> Any:
        ...

    ...
