#!/bin/bash
FIND_FILE="/opt/projManage/apprun/hypercorn.py"
FIND_STR="workers"
if [ `grep -c "$FIND_STR" $FIND_FILE` -ne '0' ];then
    echo "hypercorn config exist"
else
    cp /opt/projManage/apprun/hypercorn_default.py /opt/projManage/apprun/hypercorn.py
fi

cd /opt/projManage/backend && \
nohup /opt/projManage/venv/bin/hypercorn -c /opt/projManage/apprun/hypercorn.py main:app >> /tmp/projManage.log 2>&1 &