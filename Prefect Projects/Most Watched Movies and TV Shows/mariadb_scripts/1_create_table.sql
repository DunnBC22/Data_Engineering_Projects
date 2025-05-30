USE most_watched_movies_and_tv_shows_mariadb_db;

CREATE TABLE IF NOT EXISTS most_watched_movies_and_tv_shows_mariadb_table (
    `Rank` FLOAT,
    `Title` VARCHAR(150),
    `Type` VARCHAR(12),
    `Premiere` INTEGER,
    `Genre` VARCHAR(24),
    `Watchtime` VARCHAR(15),
    `Watchtime in Million` VARCHAR(12)
);