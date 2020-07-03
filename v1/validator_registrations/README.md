## Validator Registrations

The ValidatorRegistration model represents a connection between two validators. This can be between either:
```
CV <--> PV
CV <--> CV
```

Once a confirmation validator is registered with the primary validator it will begin receiving confirmation blocks.

## POST /validator_registrations (Client > Source Validator)

The process will begin with the client sending a request to one of their validators. Their (source) validator will then
create the pending registration and the forward the registration request to the target validator.

Request:
```json
{}
```

Response:
```json
{}
```

## POST /validator_registrations (Source Validator > Target Validator)

After receiving the registration request, the target validator will create their own validator registration which will 
be initially set to "pending". The target validator then responds to the source validator as confirmation that the 
request had been received.

The target validator will also forward the block to the primary validator (or add it to the block queue if they are the
primary validator).

Request:
```json
{}
```

Response:
```json
{}
```

## PATCH /validator_registrations/{id} (Target Validator > Source Validator)

After confirmation of payment (all validators will confirm the blocks themselves) the target validator will check that
the source validator is properly configured. This is done through the ability to act as a server by responding properly
to network requests made from the source validator to the target validators IP address. Upon configuration verification,
the source validator will send a PATCH request to inform the target validator of the registration acceptance.

Request:
```json
{}
```

Response:
```json
{}
```
