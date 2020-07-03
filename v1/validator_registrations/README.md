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
{
  "message": {
    "block": {
      "account_number": "0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb",
      "message": {
        "balance_key": "0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb",
        "txs": [
          {
            "amount": 8,
            "recipient": "ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314"
          }
        ]
      },
      "signature": "219d60986e0e0b2524ff565157c3f9e776af0c2aeaba2c4594c3082d8471c0d3adf15b57cb28e4400e85e3084d23c84db0840e99956e7723b3063d42ff96b80f"
    },
    "source_ip_address": "192.168.1.232",
    "source_node_identifier": "59479a31c3b91d96bb7a0b3e07f18d4bf301f1bb0bde05f8d36d9611dcbe7cbf",
    "source_port": 8000,
    "source_protocol": "http",
    "target_ip_address": "192.168.1.65",
    "target_node_identifier": "3afdf37573f1a511def0bd85553404b7091a76bcd79cdcebba1310527b167521",
    "target_port": 8000,
    "target_protocol": "http"
  },
  "node_identifier": "59479a31c3b91d96bb7a0b3e07f18d4bf301f1bb0bde05f8d36d9611dcbe7cbf",
  "signature": "9447eaffa91f83b10c5dee8768c48ef43e7e9a76c0c07d198c181995d5c1aad90dbdb9824fbd10e04098499940df94f28d7ce4d15a8f910bdd0d8a0247455201"
}
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
