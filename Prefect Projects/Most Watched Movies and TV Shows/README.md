# Most Watched Movies & TV Shows - Prefect Pipeline

## Description

- Rename columns
	- "Rank": "MovieRank",
	- "Title": "MovieTitle",
	- "Type": "MovieType",
	- "Premiere": "MoviePremiere",
	- "Genre": "MovieGenre",
	- "Watchtime": "MovieWatchtime",
	- "Watchtime in Million": "MovieWatchtimeInMillions"
- Handling Missing Values:
	- Fill any null values in the MoviePremiere feature with 9999
	- Fill empty strings in MovieGenre with "NotListed"
- Clean values as such:
	- Remove all commas in the MovieWatchTime feature
	- Remove the appended 'M' from all features in the MovieWatchTimeInMillions
- Convert data types:
	- Convert to integer data type:
		- MovieWatchTime
	- Convert to floating-point	numerical data type:
		- MovieWatchTimeInMillions

## Dataset Source
https://www.kaggle.com/datasets/shiivvvaam/most-watched-movies-and-tv-shows