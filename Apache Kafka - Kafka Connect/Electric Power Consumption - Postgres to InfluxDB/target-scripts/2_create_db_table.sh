#!/bin/bash
influx -execute "CREATE DATABASE epc_influx_db"
influx -execute "USE epc_influx_db"
influx -execute "CREATE RETENTION POLICY one_week_policy ON epc_influx_db DURATION 420w REPLICATION 1 DEFAULT"
