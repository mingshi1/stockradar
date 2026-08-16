from __future__ import annotations

import importlib.util
from pathlib import Path
import sys
import types


stub = types.ModuleType(
    "PySide6"
)
stub.__file__ = __file__
sys.modules["PySide6"] = stub

module_path = (
    Path(__file__)
    .resolve()
    .parent
    / "patch_pyside_android_deploy.py"
)

spec = importlib.util.spec_from_file_location(
    "patch_pyside_android_deploy",
    module_path,
)

if spec is None or spec.loader is None:
    raise RuntimeError(
        "Unable to load patch module"
    )

module = importlib.util.module_from_spec(
    spec
)
spec.loader.exec_module(
    module
)


FIXTURES = [
    """
self.set_value("app", "requirements", "python3,shiboken6,PySide6")
self.set_value("app", "p4a.branch", "develop")
""",
    """
self.set_value(
    "app",
    "requirements",
    "python3,shiboken6,PySide6,certifi==2026.7.22"
)
self.set_value("app", "p4a.branch", "develop")
""",
    """
self.set_value( 'app' , 'requirements' , 'python3,shiboken6,PySide6' )
self.set_value( 'app' , 'p4a.branch' , 'develop' )
""",
]


for index, fixture in enumerate(
    FIXTURES,
    start=1,
):
    patched = module._patch_requirements(
        fixture
    )
    patched = module._patch_p4a_branch(
        patched
    )
    module._verify(
        patched
    )

    assert "python3==3.11.15" in patched
    assert "hostpython3==3.11.15" in patched
    assert "certifi==2026.7.22" in patched
    assert "v2026.05.09" in patched

    print(
        f"fixture {index}: OK"
    )

print(
    "PySide Android deploy patch self-test: OK"
)
