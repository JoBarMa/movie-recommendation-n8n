-- Create the table with distinct directors
CREATE TABLE unique_directors AS
WITH RECURSIVE numbers AS (
  SELECT 1 AS n
  UNION ALL
  SELECT n + 1 FROM numbers WHERE n < 10
),
split_directors AS (
  SELECT
    TRIM(SUBSTRING_INDEX(SUBSTRING_INDEX(director, ',', n), ',', -1)) AS director_name
  FROM
    tmdb_movies, numbers
  WHERE
    n <= 1 + LENGTH(director) - LENGTH(REPLACE(director, ',', ''))
)
SELECT DISTINCT director_name
FROM split_directors
WHERE director_name IS NOT NULL AND director_name != '';

-- Add SOUNDEX columns to the database
DELIMITER //

CREATE PROCEDURE soundex_list(IN input TEXT)
BEGIN
  DECLARE i INT DEFAULT 1;
  DECLARE str TEXT;
  DECLARE token TEXT;
  DECLARE output TEXT DEFAULT '';
  
  SET str = input;

  WHILE LOCATE(',', str) > 0 DO
    SET token = TRIM(SUBSTRING_INDEX(str, ',', 1));
    SET output = CONCAT(output, SOUNDEX(token), ', ');
    SET str = SUBSTRING(str FROM LOCATE(',', str) + 1);
  END WHILE;
  
  -- Procesar el último elemento (sin coma)
  SET token = TRIM(str);
  SET output = CONCAT(output, SOUNDEX(token));
  
  SELECT output AS soundex_result;
END //

DELIMITER ;

DELIMITER //

CREATE FUNCTION soundex_list_func(input TEXT)
RETURNS TEXT
DETERMINISTIC
BEGIN
  DECLARE output TEXT DEFAULT '';
  DECLARE actor_name VARCHAR(255);
  DECLARE comma_pos INT DEFAULT 1;
  DECLARE next_comma_pos INT;
  DECLARE input_len INT;

  SET input_len = CHAR_LENGTH(input);

  WHILE comma_pos > 0 AND comma_pos <= input_len DO
    SET next_comma_pos = LOCATE(',', input, comma_pos);
    IF next_comma_pos > 0 THEN
      SET actor_name = TRIM(SUBSTRING(input, comma_pos, next_comma_pos - comma_pos));
      SET comma_pos = next_comma_pos + 1;
    ELSE
      SET actor_name = TRIM(SUBSTRING(input, comma_pos));
      SET comma_pos = 0; -- salir del loop
    END IF;

    IF actor_name != '' THEN
      SET output = CONCAT(output, IF(output = '', '', ','), SOUNDEX(actor_name));
    END IF;
  END WHILE;

  RETURN output;
END //

DELIMITER ;


ALTER TABLE tmdb_movies ADD COLUMN main_actors_soundex TEXT;

UPDATE tmdb_movies
SET main_actors_soundex = soundex_list_func(main_actors)

ALTER TABLE tmdb_movies ADD COLUMN title_soundex TEXT;

UPDATE tmdb_movies
SET title_soundex = SOUNDEX(title)

ALTER TABLE tmdb_movies ADD COLUMN directors_soundex TEXT;

UPDATE tmdb_movies
SET directors_soundex = soundex_list_func(director)