#!/bin/bash
docker run \
  -v ./create_agent_app/common/cutomer_support:/root/.letta/tool_execution_dir \
  -v ~/.letta/.persist/pgdata:/var/lib/postgresql/data \
  -e OPENAI_API_KEY=${OPENAI_API_KEY} \
  -p 8283:8283 \
  letta/letta:latest