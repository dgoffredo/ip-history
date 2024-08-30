create table if not exists IP(
  id integer primary key not null,
  when_first_iso text not null unique,
  when_last_iso text,
  num_checks integer not null default 1,
  v4_status integer not null,
  v4_stdout text not null,
  v4_stderr text not null,
  v6_status integer not null,
  v6_stdout integer not null,
  v6_stderr integer not null);
