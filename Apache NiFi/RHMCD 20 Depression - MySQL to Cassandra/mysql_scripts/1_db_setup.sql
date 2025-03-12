GRANT SELECT ON rhmcd20_db_mysql.* TO 'mysql'@'%';
FLUSH PRIVILEGES;

-- drop table, if exists, to start from scratch
DROP TABLE IF EXISTS rhmcd20_table_mysql;

CREATE TABLE rhmcd20_table_mysql (
	age VARCHAR(10),
	sex VARCHAR(8),
	occupation VARCHAR(12),
	days_indoors VARCHAR(21),
	growing_stress VARCHAR(6),
	quarantine_frustrations VARCHAR(6),
	changes_habits VARCHAR(6),
	mental_health_history VARCHAR(6),
	weight_change VARCHAR(6),
	mood_swings VARCHAR(8),
	coping_struggles VARCHAR(5),
	work_interest VARCHAR(8),
	social_weakness VARCHAR(8)
);