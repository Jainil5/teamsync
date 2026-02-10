import os

def project_root() -> str:
    return os.path.abspath(
        os.path.join(os.path.dirname(__file__), "..", "..")
    )


def project_path(*paths) -> str:
    return os.path.join(project_root(), *paths)
