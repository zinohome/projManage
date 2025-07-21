#!/usr/bin/env python3
# -*- coding: utf-8 -*-

loglevel = "info"
workers = 1
bind = "0.0.0.0:8843"
insecure_bind = "0.0.0.0:8880"
graceful_timeout = 120
worker_class = "uvloop"
keepalive = 5
startup_timeout = 360
errorlog = "/opt/projManage/backend/log/hypercorn_error.log"
accesslog = "/opt/projManage/backend/log/hypercorn_access.log"
keyfile = "/opt/projManage/cert/key.pem"
certfile = "/opt/projManage/cert/cert.pem"