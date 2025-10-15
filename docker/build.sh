#!/bin/bash
IMGNAME=tls/projmanage
IMGVERSION=v0.1.6
docker build --no-cache -t $IMGNAME:$IMGVERSION .