"""ip-history

Query the myip.opendns.com A and AAAA record from one of the opendns.com DNS
resolvers and update a local SQLite database with the resulting values.

myip.opendns.com resolves to the public IP address of the caller.

For example:

    $ python .
    $ sqlite3 -line db.sqlite 'select * from IP'
                id = 1
    when_first_iso = 2024-08-30T15:06:17.785706+00:00
     when_last_iso =
        num_checks = 1
         v4_status = 0
         v4_stdout = 24.90.211.230
         v4_stderr =
         v6_status = 0
         v6_stdout = 2603:7000:5101:de1c:8bd1:593f:a043:c39a
         v6_stderr =

This script invokes the `dig` command line utility from the POSIX command shell
(/bin/sh).
"""

import argparse
import datetime
import importlib.resources
from pathlib import Path
import sqlite3
import subprocess
import sys


def parse_options(args):
  parser = argparse.ArgumentParser(
      prog='python ip-history/',
      description="Save the host's public IP to a SQLite database.")
  parser.add_argument('database',
      nargs='?',
      type=Path,
      default=Path(__file__).parent/'db.sqlite')
  return parser.parse_args(args)


def persist(db_path, ipv4_result, ipv6_result):
  sql_files = importlib.resources.files('sql')
  db = sqlite3.connect(db_path)
  now = datetime.datetime.now(tz=datetime.timezone.utc).isoformat()

  schema = (sql_files/'schema.sql').read_text()
  with db:
    db.execute(schema)
  with db:
    select_latest = (sql_files/'select-latest.sql').read_text()
    rows = list(db.execute(select_latest))
    if len(rows) != 0:
      (rowid, v4_status, v4_stdout, v4_stderr, v6_status, v6_stdout, v6_stderr), = rows
      if (v4_status == ipv4_result.returncode and
          v4_stdout == ipv4_result.stdout and
          v4_stderr == ipv4_result.stderr and
          v6_status == ipv6_result.returncode and
          v6_stdout == ipv6_result.stdout and
          v6_stderr == ipv6_result.stderr):
        update_latest = (sql_files/'update-latest.sql').read_text()
        db.execute(update_latest, {
          'when_last_iso': now,
          'id': rowid
        })
        return

    insert_latest = (sql_files/'insert-latest.sql').read_text()
    db.execute(insert_latest, {
      'when_first_iso': now,
      'v4_status': ipv4_result.returncode,
      'v4_stdout': ipv4_result.stdout,
      'v4_stderr': ipv4_result.stderr,
      'v6_status': ipv6_result.returncode,
      'v6_stdout': ipv6_result.stdout,
      'v6_stderr': ipv6_result.stderr
    })


def execute_shell_script(script, *args):
  result = subprocess.run(
      ['/bin/sh', '-s', '--', *args],
      input=script,
      encoding='utf8',
      capture_output=True)
  result.stdout = result.stdout.strip()
  result.stderr = result.stderr.strip()
  return result


def main(argv):
  options = parse_options(argv[1:])

  myip_script = (importlib.resources.files('sh')/'myip').read_text()
  ipv4_result = execute_shell_script(myip_script)
  ipv6_result = execute_shell_script(myip_script, '-6')
  persist(options.database, ipv4_result, ipv6_result)
  return 0


if __name__ == '__main__':
  sys.exit(main(sys.argv))
