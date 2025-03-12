CREATE KEYSPACE rhmcd20_keyspace_cassandra WITH replication = {'class': 'SimpleStrategy', 'replication_factor': 1};

CREATE TABLE rhmcd20_keyspace_cassandra.rhmcd20_table_cassandra (
	id INT,
    age VARCHAR,
	sex VARCHAR,
	occupation VARCHAR,
	days_indoors VARCHAR,
	growing_stress VARCHAR,
	quarantine_frustrations VARCHAR,
	changes_habits VARCHAR,
	mental_health_history VARCHAR,
	weight_change VARCHAR,
	mood_swings VARCHAR,
	coping_struggles VARCHAR,
	work_interest VARCHAR,
	social_weakness VARCHAR,
	PRIMARY KEY (ID)
);