from thenewboston.models.network_transaction import NetworkTransaction


class Transaction(NetworkTransaction):

    class Meta:
        default_related_name = 'transactions'

    def __str__(self):
        return (
            f'ID: {self.id} | '
            f'Sender: {self.sender} | '
            f'Recipient: {self.recipient} | '
            f'Amount: {self.amount}'
        )
