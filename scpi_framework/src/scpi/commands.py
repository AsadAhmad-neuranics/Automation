class Command:
    def __init__(self, instrument):
        self.instrument = instrument

    def execute(self, command):
        self.instrument.send_command(command)
        response = self.instrument.receive_response()
        return response

    def query(self, command):
        self.instrument.send_command(command)
        return self.instrument.receive_response()
    