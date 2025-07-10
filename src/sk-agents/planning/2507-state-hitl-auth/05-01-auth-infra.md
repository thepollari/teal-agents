# Phase 5 - Authorization Overview

This document provides an overview of how the new authorization system will work for
Teal Agents. Initially, it will only focus on OAuth 2.0, the design should be extensible
to support other authorization types in the future.

## Overview

The existing auth setup for teal agents is rudimentary and not scalable. As such, we
will refactor and include the ability for the platform to dynamically understand the
auth requirements for a particular tool and, when required, prompt the calling client
to prompt the user to perform the appropriate authorization flow. We will begin with
OAuth 2.0. The internal flow will go something like:

1. Agent decides to use a tool
2. Agent platform intercepts tool call response from LLM and retrieves the tool metadata
   from the tool catalog (see phase 4)
3. If the tool requires authorization (for now, OAuth 2.0), the platform will search for
   an existing token for the given authorization server and scopes for this user within
   the "Secure Auth Storage Service"
4. If the token exists, it will be used to invoke the tool
5. If the token does not exist, a new response type will be crafted and returned that
   indicates to the client that the user needs to perform the appropriate authorization
   flow. Note that the flow must be initiated from the agent platform (or at a minimum)