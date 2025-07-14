#!/bin/bash
FIND_FILE="/opt/projManage/apprun/gunicorn.py"
FIND_STR="workers"
if [ `grep -c "$FIND_STR" $FIND_FILE` -ne '0' ];then
    echo "gunicorn config exist"
else
    cp /opt/projManage/apprun/gunicorn_default.py /opt/projManage/config/gunicorn.py
fi
cd /opt/projManage/backend && \
nohup /opt/projManage/venv/bin/gunicorn -c /opt/projManage/apprun/gunicorn.py main:app >> /tmp/projManage.log 2>&1 &