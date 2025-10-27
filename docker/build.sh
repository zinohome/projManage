#!/bin/bash
IMGNAME=tls/projmanage
IMGVERSION=v0.2.1
docker build --no-cache -t $IMGNAME:$IMGVERSION .