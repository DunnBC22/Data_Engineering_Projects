-- database name: fb_google_reviews_db
-- owner: airflow;

CREATE TABLE IF NOT EXISTS fb_google_reviews (
	review_id VARCHAR,
    pseudo_author_id VARCHAR,
    author_name VARCHAR,
    review_text VARCHAR,
    review_rating INTEGER,
    review_likes INTEGER,
    author_app_version VARCHAR,
    review_timestamp TIMESTAMP
);

GRANT SELECT, INSERT, UPDATE, DELETE ON TABLE fb_google_reviews TO airflow;

COPY fb_google_reviews(
    review_id, 
    pseudo_author_id, 
    author_name, 
    review_text, 
    review_rating, 
    review_likes, 
    author_app_version, 
    review_timestamp
    )
FROM '/Users/briandunn/Desktop/Projects 2/Facebook Google Store Reviews 4.1 Million/FACEBOOK_REVIEWS.csv'
DELIMITER ','
CSV HEADER;