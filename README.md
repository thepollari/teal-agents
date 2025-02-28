# Teal Agents Platform
## Overview
The Agent Platform aims to provide two major sets of functionality:
1. A core framework for creating and deploying individual agents
2. A set of orchestrators (and supporting services) which allow you to compose
   multiple agents for more complex use cases

## Core Agent Framework
The core framework can be found in the src/sk-agents directory. For more 
information, see its [README.md](src/sk-agents/README.md).

## Orchestrators
Orchestrators provide the patterns in which agents are grouped and interact with
both each other and the applications which leverage them. For more information
on orchestrators, see [README.md](src/orchestrators/README.md).

## Getting Started
Regardless of if you're experimenting with individual agents or orchestrators,
or contributing to the developent of the platform, you'll need to build the base
images. To do so, once cloning this repository locally, from the root directory
run:
```bash
$ git clone https://github.com/MSDLLCpapers/teal-agents.git
$ cd teal-agents
$ make all
```
