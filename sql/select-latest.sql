select
  id,
  v4_status,
  v4_stdout,
  v4_stderr,
  v6_status,
  v6_stdout,
  v6_stderr
from IP
order by when_first_iso desc
limit 1;
