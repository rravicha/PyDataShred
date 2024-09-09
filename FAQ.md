Database: mysql
codespace:
- Command: 'sudo systemctl start mysql.service'
  Error: 'systemctl cannot be invoked due to overload'
  Workaround: 'sudo service mysql start '
  CreatedBy: 'Raghav'
  Detected: 'Phase 1 |mysql installation'
  Description: 'Error faced post installing mysql in codespace and trying to start the service'

Credentials for DB:
  {'username':'scott', 'password':'tiger'}

this is just for temp storage, ignore and alway keep at end of this file
setup(
      name='datashredpy',
      version='0.0.1',
      author='datashred team'
      author_email='rravicha.gmail.com',
      description='data shred framework'
      keywords=['python','datashred','datamesh','datafabric','etl','ingestion']
      packages=find_packages(),
      install_requires=[],
      package_data=_expand_recursive_globs({
          "datashredpy": ["*"]
      }),
      zip_safe=False
      )
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

[pypi]
  username = __token__
  password = pypi-AgEIcHlwaS5vcmcCJGE5YjZiN2YzLTIzMjAtNGNiNS04YjIzLWZiMjMzOWFlNDdlNwACKlszLCI3ODkyNjNiYy1mN2ZhLTQ3MWEtYmU0NS05OTA0YmFmMjJlMmQiXQAABiBm_qTLMqY8Zsu_u0kRBYeTEerBvzifgBqXTo4E5y5RbQ