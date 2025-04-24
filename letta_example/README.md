# Letta Example

## Running the Letta server 
Letta is a service-oriented framework, so you need to run a Letta server to create agents. The server needs external files mounted into the Docker container to access them: 
``` 
# make sure you are in the ./create-agent-app directory
cd .. 

# configure keys 
export OPENAI_API_KEY=...

# run the docker command 
docker run \
  -v $PWD/create_agent_app:/app/create_agent_app \ # mount code directory
  -v ~/.letta/.persist/pgdata:/var/lib/postgresql/data \
  -e OPENAI_API_KEY=${OPENAI_API_KEY} \
  -p 8283:8283 \
  letta/letta:latest
```

## Creating the agent 
Create the example agent using the client-side script: 
```
cd letta_example
pip install -r requirements.txt
python customer_support_agent.py
```

## Using the ADE
