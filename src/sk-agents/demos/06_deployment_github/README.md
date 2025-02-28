# Teal Agents Framework
## Deployment from Github
For most common use cases, you will not need to work with this repo directly
for anything other than debugging if you're writing custom code. Rather, you
will store all of your agent configuration, custom_plugins/types.py, and
requirements files in an agent-specific folder in a separate Github repository.

When the agent starts up with your configuration, the Teal Agents framework will
automatically download your agent configuration and start the agent from the
existing framework container.

### Testing it out locally
In this demonstration, we'll make use of an existing agent configuration from
the shared repository, the **TODO - Replace with demo repo when available on Github**

For reference, the configuration in the shared repo is the same as that found in
demo 03_plugins.

In order to run this demonstration, you'll need to set up your environment file
(`.env`) to contain the following:
```text
TA_API_KEY=<Your API Key>
TA_GITHUB=true
TA_GH_ORG=TBD
TA_GH_REPO=TBD
TA_GH_BRANCH=main
TA_AGENT_NAME=ChatWeatherAgent
TA_GH_TOKEN=<Your Github Personal Access Token>
DOCKER_USERNAME=<Your Docker Username>
DOCKER_PASSWORD=<Your Docker Password>
```

* TA_API_KEY - Same as for other use cases, enter your appropriate API key
* TA_GITHUB - Set to true to indicate that your agent configuration resides
  in a shared github repository
* TA_GH_ORG - The github organization that contains the shared agent
  configurations
* TA_GH_REPO - The repository within the organization that contains the shared
  agent configurations
* TA_GH_BRANCH - The branch within the repository that contains the shared
  agent configurations
* TA_AGENT_NAME - The name of the agent configuration folder within the
  repository
* TA_GH_TOKEN - A github personal access token with read access to the
  repository
* DOCKER_USERNAME - The docker username to pull the base sk-agents image
* DOCKER_PASSWORD - The docker password to pull the base sk-agents image

To run this example, you'll need `docker compose` installed on your machine.
After setting up your environment file, simply run `docker compose up -d`. The
agent will start on port 8000 and can be accessed via
http://localhost:8000/docs.