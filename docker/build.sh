#!/bin/bash
IMGNAME=tls/projmanage
IMGVERSION=v0.2.0
docker build --no-cache -t $IMGNAME:$IMGVERSION .