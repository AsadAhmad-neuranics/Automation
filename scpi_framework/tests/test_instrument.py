import unittest
from scpi_framework.src.scpi.instruments import Instrument

class TestInstrument(unittest.TestCase):

    def setUp(self):
        self.instrument = Instrument()

    def test_connect(self):
        self.assertTrue(self.instrument.connect())
        self.assertTrue(self.instrument.is_connected)

    def test_disconnect(self):
        self.instrument.connect()
        self.instrument.disconnect()
        self.assertFalse(self.instrument.is_connected)

    def test_send_command(self):
        self.instrument.connect()
        response = self.instrument.send_command('*IDN?')
        self.assertIsInstance(response, str)  # Assuming the response is a string
        self.instrument.disconnect()

if __name__ == '__main__':
    unittest.main()