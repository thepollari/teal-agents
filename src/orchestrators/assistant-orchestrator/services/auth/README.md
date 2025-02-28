# Teal Agent Platform - Orchestrator Services
## Authentication

By default, authentication for the assistant orchestrator is not secure and all
that is required is a request with a payload containing a user ID of the format:

```json
{
  "user_id": "1234567890"
}
```

Because user authentication comes in many forms, assistant orchestrator
authentication is customizable. To implement custom authentication, you'll need
to create a custom module and make it available to the running services
instance. Within the module, you'll need to provide both a request payload class
which inherits from Pydantic's BaseModel as well as an implementation of the 
abstract class `Authenticator`.

### Request Payload
The request payload class must contain all information required to successfully
authenticate and authorize a user to use this instance of the assistant
orchestrator.

### Authenticator
The Authenticator class must implement the following methods:
* `authenticate` - This method accepts a payload of the defined request payload
  type and returns an instance of `AuthResponse` which contains two fields:
  * `success` (bool) - Whether or not the authentication attempt was successful
  * `user_id` (str) - A string identifying the authenticated user

This class should always return a response of the specified type and not raise
exceptions in cases of authentication failure (that is handled higher up in the
application.

### Configuration
To leverage your custom authentication, you'll need to provide the following
environment variables:
* `TA_CUSTOM_AUTH_ENABLED` - Set to `true` to activate your custom
  authentication
* `TA_CUSTOM_AUTH_MODULE` - The relative path to the python module containing
  your custom authentication implementation (payload and class)
* `TA_CUSTOM_AUTHENTICATOR` - The name of your implementation of the\
  `Authenticator` class
* `TA_CUSTOM_AUTH_REQUEST` - The name of your implementation of the request
  payload class

### Example
An [example implementation](custom/example_custom_authenticator.py) of custom
authentication can be found in the `custom` subdirectory. In this example, the
request payload still only contains a user ID but the authenticator will only
successfully authenticate users with the ID `good_id`.