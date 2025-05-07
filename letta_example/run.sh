#!/bin/bash
docker run \
  -v $PWD/create_agent_app:/app/create_agent_app \
  -v ~/.letta/.persist/pgdata:/var/lib/postgresql/data \
  -e GEMINI_API_KEY=${GEMINI_API_KEY} \
  -p 8283:8283 \
  letta/letta:latest
