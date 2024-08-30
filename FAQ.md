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
