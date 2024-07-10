#!/bin/bash
influx -execute "CREATE USER influx_kafka_user WITH PASSWORD 'influx_kafka_password' WITH ALL PRIVILEGES"