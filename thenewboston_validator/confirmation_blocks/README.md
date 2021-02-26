## Confirmation blocks

Confirmation blocks are blocks signed by a validator representing that the related block and all transactions have been 
confirmed.

```json
{
  "message": {
    "block": {
      "account_number": "0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb",
      "message": {
        "balance_key": "0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb",
        "txs": [
          {
            "amount": 1,
            "recipient": "484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc"
          },
          {
            "amount": 1,
            "recipient": "5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8"
          },
          {
            "amount": 4,
            "recipient": "ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314"
          }
        ]
      },
      "signature": "98f604d2db6fb5c70fdfe4d0ecbc47d56a77ff8320319d102d0c9bd0720516dc826a70735d4b6cdfc331d7cf13bd9de73250060230c01389e442009741a20e0e"
    },
    "block_identifier": "4694e1ee1dcfd8ee5f989e59ae40a9f751812bf5ca52aca2766b322c4060672b",
    "updated_balances": [
      {
        "account_number": "0cdd4ba04456ca169baca3d66eace869520c62fe84421329086e03d91a68acdb",
        "balance": "9994",
        "balance_lock": "b2cab62f3432553d2f0b765b7f1d67ea8d2a9b02948d0912ac8c8317553bbe28"
      },
      {
        "account_number": "484b3176c63d5f37d808404af1a12c4b9649cd6f6769f35bdf5a816133623fbc",
        "balance": "1001"
      },
      {
        "account_number": "5e12967707909e62b2bb2036c209085a784fabbc3deccefee70052b6181c8ed8",
        "balance": "51"
      },
      {
        "account_number": "ad1f8845c6a1abb6011a2a434a079a087c460657aad54329a84b406dce8bf314",
        "balance": "54"
      }
    ]
  },
  "node_identifier": "3afdf37573f1a511def0bd85553404b7091a76bcd79cdcebba1310527b167521",
  "signature": "8dc104e0085a81a5fe48916a3ed81e0534720c1c2fa2c9d509b06747ef0217d05affbef25f88a9d65b40500ca9f19c8706c05899af945fe1e20a944cd7084d02"
}
```
