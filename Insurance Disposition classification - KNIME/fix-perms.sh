#!/bin/sh

# This will be run as root during container startup
chown -R 1001:1001 /home/knime_user/upload
chmod -R 755 /home/knime_user/upload