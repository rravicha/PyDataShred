from pathlib import Path
from typing import Dict, List
from setuptools import setup, find_packages
import os


def _expand_recursive_globs(package_data: Dict[str, List[str]]) -> Dict[str, List[str]]:
    root = Path(__file__).parent.resolve()
    for module, patterns in package_data.items():
        new_patterns = []
        m_root = None
        for idx, p in enumerate(patterns):
            if "**" in p:
                m_root = m_root or root / module.replace(".", os.sep)
                for f in m_root.glob("**"):  # all subdirectories
                    if f.name == "__pycache__":
                        continue
                    subdir_pattern = p.replace("**", str(f.relative_to(m_root)))
                    new_patterns.append(subdir_pattern)
            else:
                new_patterns.append(p)
        package_data[module] = new_patterns
    return package_data


setup(
      packages=find_packages(),
      install_requires=[],
      )
