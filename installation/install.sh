#!/bin/bash
/bin/sh install-packets.sh
sudo -u postgres psql -f create-db.sql
sudo -u postgres psql -d stake -f create-tables.sql
