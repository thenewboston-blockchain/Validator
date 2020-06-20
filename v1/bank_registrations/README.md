## Bank Registrations

Banks must also register with validators before they are accepted onto the network by that validator. This is done in a 
similar fashion to the registration process between user accounts and banks. To register, banks will pay a registration 
fee to the validator. The validator will then place the registration in a "pending" state as it performs a network 
background check of the applying bank. During this process, validators will check the bank's trust level with other 
existing banks. Banks must also prove that they are configured properly to act as a bank node. This is done through the 
ability to act as a server by responding properly to network requests made from the validator to the bank's IP address. 
This verification prevents end users from acting as banks by sending transactions directly to the validator.

### POST /bank_registrations

Request (Bank > Validator):
```json
{
  "message": {
    "block": {
      "account_number": "5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8",
      "message": {
        "balance_key": "5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8",
        "txs": [
          {
            "amount": 8,
            "recipient": "ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314"
          }
        ]
      },
      "signature": "a341eb2d678df410fb110760fd2c77c5969975d4fcba9a3846d9f11dfb43151bc23a157c26dd29163f061697806bc2b75d74a300ed6ba1a504ae2de6013d8c0f"
    },
    "ip_address": "192.168.1.232",
    "port": 8000,
    "protocol": "http",
    "validator_network_identifier": "3afdf37573f1a511def0bd85553404b7091a76bcd79cdcebba1310527b167521",
    "version": "v1.0"
  },
  "network_identifier": "d5356888dc9303e44ce52b1e06c3165a7759b9df1e6a6dfbd33ee1c3df1ab4d1",
  "signature": "890d200626e4403702f15bb00906d5d8f4abba2cab68cec37007d6436f9256e202d2e26a049ad0e68d5c07cea7db7c20cb346b15ac973f909bac0df8f605f60c"
}
```

### PATCH /bank_registrations

- `message` - status to indicate the result of the bank registration
- `network_identifier` - network identifier of the primary validator
- `signature` - hex value of the signed `message`

Request (Validator > Bank):
```json
{
  "message": {
    "status": "ACCEPTED"
  },
  "network_identifier": "3afdf37573f1a511def0bd85553404b7091a76bcd79cdcebba1310527b167521",
  "signature": "11773d39c58cf99f60c0bda385a5ac1135c0c0246554cedded78ce68896c00ac851413543d77aa6aeefc76ef2f9962301a370c934be5c0d88d3b8cc0e6fc0f09"
}
```

Response (Bank > Validator):
```json
{
  "id":"36f84a29-cdd5-442a-88bc-fbc4107e5207",
  "created_date":"2020-06-20T17:31:38.578363Z",
  "modified_date": "2020-06-21T22:17:56.705678Z",
  "fee":"8.0000000000000000",
  "status": "ACCEPTED",
  "validator": "a8101b03-15ad-42fc-8e64-2de24b850e0e"
}
```