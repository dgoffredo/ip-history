update IP set
  num_checks = num_checks + 1,
  when_last_iso = :when_last_iso
  where id = :id;
