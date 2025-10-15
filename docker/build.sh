#!/bin/bash
IMGNAME=tls/projmanage
IMGVERSION=v0.1.7
docker build --no-cache -t $IMGNAME:$IMGVERSION .