import unittest
from unittest.mock import MagicMock, patch
import grpc
from crac_client.retriever.roof_retriever import RoofRetriever
from crac_client.retriever.telescope_retriever import TelescopeRetriever
from crac_client.retriever.weather_retriever import WeatherRetriever
from crac_client.retriever.button_retriever import ButtonRetriever
from crac_client.retriever.curtains_retriever import CurtainsRetriever
from crac_client.retriever.ups_retriever import UpsRetriever
from crac_client.converter.converter import Converter

class TestRetrieverChannels(unittest.TestCase):

    def setUp(self):
        self.mock_converter = MagicMock(spec=Converter)
        self.mock_channel = MagicMock(spec=grpc.Channel)

    @patch('grpc.insecure_channel')
    def test_roof_retriever_uses_shared_channel(self, mock_insecure_channel):
        """RoofRetriever should use the provided channel and not create a new one."""
        retriever = RoofRetriever(self.mock_converter, channel=self.mock_channel)
        
        self.assertEqual(retriever.channel, self.mock_channel)
        mock_insecure_channel.assert_not_called()

    @patch('grpc.insecure_channel')
    def test_roof_retriever_creates_default_channel(self, mock_insecure_channel):
        """RoofRetriever should create a new channel if none is provided."""
        # Mock Config to avoid issues with missing config.ini
        with patch('crac_client.config.Config.getValue', return_value='localhost'):
            retriever = RoofRetriever(self.mock_converter, channel=None)
            
            self.assertIsNotNone(retriever.channel)
            mock_insecure_channel.assert_called_once()

    @patch('grpc.insecure_channel')
    def test_telescope_retriever_uses_shared_channel(self, mock_insecure_channel):
        retriever = TelescopeRetriever(self.mock_converter, channel=self.mock_channel)
        self.assertEqual(retriever.channel, self.mock_channel)
        mock_insecure_channel.assert_not_called()

    @patch('grpc.insecure_channel')
    def test_weather_retriever_uses_shared_channel(self, mock_insecure_channel):
        retriever = WeatherRetriever(self.mock_converter, channel=self.mock_channel)
        self.assertEqual(retriever.channel, self.mock_channel)
        mock_insecure_channel.assert_not_called()

    @patch('grpc.insecure_channel')
    def test_button_retriever_uses_shared_channel(self, mock_insecure_channel):
        retriever = ButtonRetriever(self.mock_converter, channel=self.mock_channel)
        self.assertEqual(retriever.channel, self.mock_channel)
        mock_insecure_channel.assert_not_called()

    @patch('grpc.insecure_channel')
    def test_curtains_retriever_uses_shared_channel(self, mock_insecure_channel):
        retriever = CurtainsRetriever(self.mock_converter, channel=self.mock_channel)
        self.assertEqual(retriever.channel, self.mock_channel)
        mock_insecure_channel.assert_not_called()

    @patch('grpc.insecure_channel')
    def test_ups_retriever_uses_shared_channel(self, mock_insecure_channel):
        retriever = UpsRetriever(self.mock_converter, channel=self.mock_channel)
        self.assertEqual(retriever.channel, self.mock_channel)
        mock_insecure_channel.assert_not_called()

if __name__ == '__main__':
    unittest.main()
