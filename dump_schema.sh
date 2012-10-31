mysqldump --no-data --events --triggers --routines --default-character-set=utf8 -B from_schema > from_schema.sql
mysqldump --no-data --events --triggers --routines --default-character-set=utf8 -B to_schema > to_schema.sql
