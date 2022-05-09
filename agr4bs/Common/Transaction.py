class Payload(object):

    def __init__(self, data: str = None):

        if data is None:
            data = ""

        if type(data) is not str:
            raise TypeError(
                "Invalid Payload data type. Got {} expected str".format(type(data)))

        self._data = data

    @property
    def data(self) -> str:
        return self._data

    def serialize(self) -> str:
        return self._data

    def __str__(self) -> str:
        return self.serialize()


class Transaction(object):

    def __init__(self, origin: str, destination: str, amount: int = 0, fee: int = 0, payload: Payload = None) -> None:
        self._origin = origin
        self._destination = destination
        self._amount = amount
        self._fee = fee

        if payload is None:
            payload = Payload()

        self._payload = payload

    @property
    def origin(self) -> str:
        return self._origin

    @property
    def destination(self) -> str:
        return self._destination

    @property
    def amount(self) -> int:
        return self._amount

    @property
    def fee(self) -> int:
        return self._fee

    @property
    def payload(self) -> Payload:
        return self._payload

    def __str__(self) -> str:
        return self.serialize()

    def serialize(self) -> str:
        return "{{ from: {} - to: {} - fee: {} - amount: {} - payload: {} }}".format(self._origin, self._destination, str(self.fee).zfill(10), str(self.amount).zfill(10), self._payload.serialize())
