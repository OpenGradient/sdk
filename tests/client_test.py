import json
import os
import sys
from unittest.mock import MagicMock, mock_open, patch

import pytest

sys.path.append(os.path.join(os.path.dirname(__file__), ".."))

from src.opengradient.client import Client
from src.opengradient.types import (
    TEE_LLM,
    StreamChunk,
    TextGenerationOutput,
    x402SettlementMode,
)

# --- Fixtures ---


@pytest.fixture
def mock_web3():
    """Create a mock Web3 instance."""
    with patch("src.opengradient.client.client.Web3") as mock:
        mock_instance = MagicMock()
        mock.return_value = mock_instance
        mock.HTTPProvider.return_value = MagicMock()

        mock_instance.eth.account.from_key.return_value = MagicMock(address="0x1234567890abcdef1234567890abcdef12345678")
        mock_instance.eth.get_transaction_count.return_value = 0
        mock_instance.eth.gas_price = 1000000000
        mock_instance.eth.contract.return_value = MagicMock()

        yield mock_instance


@pytest.fixture
def mock_abi_files():
    """Mock ABI file reads."""
    inference_abi = [{"type": "function", "name": "run", "inputs": [], "outputs": []}]
    precompile_abi = [{"type": "function", "name": "infer", "inputs": [], "outputs": []}]

    def mock_file_open(path, *args, **kwargs):
        if "inference.abi" in str(path):
            return mock_open(read_data=json.dumps(inference_abi))()
        elif "InferencePrecompile.abi" in str(path):
            return mock_open(read_data=json.dumps(precompile_abi))()
        return mock_open(read_data="{}")()

    with patch("builtins.open", side_effect=mock_file_open):
        yield


@pytest.fixture
def client(mock_web3, mock_abi_files):
    """Create a Client instance with mocked dependencies."""
    return Client(
        private_key="0x" + "a" * 64,
        rpc_url="https://test.rpc.url",
        api_url="https://test.api.url",
        contract_address="0x" + "b" * 40,
    )


# --- Client Initialization Tests ---


class TestClientInitialization:
    def test_client_initialization_without_auth(self, mock_web3, mock_abi_files):
        """Test basic client initialization without authentication."""
        client = Client(
            private_key="0x" + "a" * 64,
            rpc_url="https://test.rpc.url",
            api_url="https://test.api.url",
            contract_address="0x" + "b" * 40,
        )

        assert client.model_hub._hub_user is None

    def test_client_initialization_with_auth(self, mock_web3, mock_abi_files):
        """Test client initialization with email/password authentication."""
        with (
            patch("src.opengradient.client.model_hub._FIREBASE_CONFIG", {"apiKey": "fake"}),
            patch("src.opengradient.client.model_hub.firebase") as mock_firebase,
        ):
            mock_auth = MagicMock()
            mock_auth.sign_in_with_email_and_password.return_value = {
                "idToken": "test_token",
                "email": "test@test.com",
            }
            mock_firebase.initialize_app.return_value.auth.return_value = mock_auth

            client = Client(
                private_key="0x" + "a" * 64,
                rpc_url="https://test.rpc.url",
                api_url="https://test.api.url",
                contract_address="0x" + "b" * 40,
                email="test@test.com",
                password="test_password",
            )

            assert client.model_hub._hub_user is not None
            assert client.model_hub._hub_user["idToken"] == "test_token"

    def test_client_initialization_custom_llm_urls(self, mock_web3, mock_abi_files):
        """Test client initialization with custom LLM server URLs."""
        custom_llm_url = "https://custom.llm.server"
        custom_streaming_url = "https://custom.streaming.server"

        client = Client(
            private_key="0x" + "a" * 64,
            rpc_url="https://test.rpc.url",
            api_url="https://test.api.url",
            contract_address="0x" + "b" * 40,
            og_llm_server_url=custom_llm_url,
            og_llm_streaming_server_url=custom_streaming_url,
        )

        assert client.llm._og_llm_server_url == custom_llm_url
        assert client.llm._og_llm_streaming_server_url == custom_streaming_url


class TestAlphaProperty:
    def test_alpha_initialized_on_client_creation(self, client):
        """Test that alpha is initialized during client creation."""
        assert client.alpha is not None

    def test_alpha_has_infer_method(self, client):
        """Test that alpha namespace has the infer method."""
        assert hasattr(client.alpha, "infer")


# --- Authentication Tests ---


class TestAuthentication:
    def test_login_to_hub_success(self, mock_web3, mock_abi_files):
        """Test successful login to hub."""
        with (
            patch("src.opengradient.client.model_hub._FIREBASE_CONFIG", {"apiKey": "fake"}),
            patch("src.opengradient.client.model_hub.firebase") as mock_firebase,
        ):
            mock_auth = MagicMock()
            mock_auth.sign_in_with_email_and_password.return_value = {
                "idToken": "success_token",
                "email": "user@test.com",
            }
            mock_firebase.initialize_app.return_value.auth.return_value = mock_auth

            client = Client(
                private_key="0x" + "a" * 64,
                rpc_url="https://test.rpc.url",
                api_url="https://test.api.url",
                contract_address="0x" + "b" * 40,
                email="user@test.com",
                password="password123",
            )

            mock_auth.sign_in_with_email_and_password.assert_called_once_with("user@test.com", "password123")
            assert client.model_hub._hub_user["idToken"] == "success_token"

    def test_login_to_hub_failure(self, mock_web3, mock_abi_files):
        """Test login failure raises exception."""
        with (
            patch("src.opengradient.client.model_hub._FIREBASE_CONFIG", {"apiKey": "fake"}),
            patch("src.opengradient.client.model_hub.firebase") as mock_firebase,
        ):
            mock_auth = MagicMock()
            mock_auth.sign_in_with_email_and_password.side_effect = Exception("Invalid credentials")
            mock_firebase.initialize_app.return_value.auth.return_value = mock_auth

            with pytest.raises(Exception, match="Invalid credentials"):
                Client(
                    private_key="0x" + "a" * 64,
                    rpc_url="https://test.rpc.url",
                    api_url="https://test.api.url",
                    contract_address="0x" + "b" * 40,
                    email="user@test.com",
                    password="wrong_password",
                )


# --- LLM Tests ---


class TestLLMCompletion:
    def test_llm_completion_success(self, client):
        """Test successful LLM completion."""
        with patch.object(client.llm, "_tee_llm_completion") as mock_tee:
            mock_tee.return_value = TextGenerationOutput(
                transaction_hash="external",
                completion_output="Hello! How can I help?",
                payment_hash="0xpayment123",
            )

            result = client.llm.completion(
                model=TEE_LLM.GPT_4O,
                prompt="Hello",
                max_tokens=100,
            )

            assert result.completion_output == "Hello! How can I help?"
            mock_tee.assert_called_once()


class TestLLMChat:
    def test_llm_chat_success_non_streaming(self, client):
        """Test successful non-streaming LLM chat."""
        with patch.object(client.llm, "_tee_llm_chat") as mock_tee:
            mock_tee.return_value = TextGenerationOutput(
                transaction_hash="external",
                chat_output={"role": "assistant", "content": "Hi there!"},
                finish_reason="stop",
                payment_hash="0xpayment",
            )

            result = client.llm.chat(
                model=TEE_LLM.GPT_4O,
                messages=[{"role": "user", "content": "Hello"}],
                stream=False,
            )

            assert result.chat_output["content"] == "Hi there!"
            mock_tee.assert_called_once()

    def test_llm_chat_streaming(self, client):
        """Test streaming LLM chat."""
        with patch.object(client.llm, "_tee_llm_chat_stream_sync") as mock_stream:
            mock_chunks = [
                StreamChunk(choices=[], model="gpt-4o"),
                StreamChunk(choices=[], model="gpt-4o", is_final=True),
            ]
            mock_stream.return_value = iter(mock_chunks)

            result = client.llm.chat(
                model=TEE_LLM.GPT_4O,
                messages=[{"role": "user", "content": "Hello"}],
                stream=True,
            )

            chunks = list(result)
            assert len(chunks) == 2
            mock_stream.assert_called_once()


# --- StreamChunk Tests ---


class TestStreamChunk:
    def test_from_sse_data_basic(self):
        """Test parsing basic SSE data."""
        data = {
            "model": "gpt-4o",
            "choices": [
                {
                    "index": 0,
                    "delta": {"content": "Hello"},
                    "finish_reason": None,
                }
            ],
        }

        chunk = StreamChunk.from_sse_data(data)

        assert chunk.model == "gpt-4o"
        assert len(chunk.choices) == 1
        assert chunk.choices[0].delta.content == "Hello"
        assert not chunk.is_final

    def test_from_sse_data_with_finish_reason(self):
        """Test parsing SSE data with finish reason."""
        data = {
            "model": "gpt-4o",
            "choices": [
                {
                    "index": 0,
                    "delta": {},
                    "finish_reason": "stop",
                }
            ],
        }

        chunk = StreamChunk.from_sse_data(data)

        assert chunk.is_final
        assert chunk.choices[0].finish_reason == "stop"

    def test_from_sse_data_with_usage(self):
        """Test parsing SSE data with usage info."""
        data = {
            "model": "gpt-4o",
            "choices": [],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 20,
                "total_tokens": 30,
            },
        }

        chunk = StreamChunk.from_sse_data(data)

        assert chunk.usage is not None
        assert chunk.usage.prompt_tokens == 10
        assert chunk.usage.total_tokens == 30
        assert chunk.is_final


# --- x402 Settlement Mode Tests ---


class TestX402SettlementMode:
    def test_settlement_modes_values(self):
        """Test settlement mode enum values."""
        assert x402SettlementMode.SETTLE == "settle"
        assert x402SettlementMode.SETTLE_BATCH == "settle-batch"
        assert x402SettlementMode.SETTLE_METADATA == "settle-metadata"

    def test_settlement_mode_aliases(self):
        """Test settlement mode aliases."""
        assert x402SettlementMode.SETTLE_INDIVIDUAL == x402SettlementMode.SETTLE
        assert x402SettlementMode.SETTLE_INDIVIDUAL_WITH_METADATA == x402SettlementMode.SETTLE_METADATA


class TestResponseFormatValidation:
    """Test response_format validation logic."""

    @pytest.fixture
    def client(self, mock_web3, mock_abi_files):
        """Create a test client instance."""
        return Client(private_key="0x" + "1" * 64)

    def test_none_response_format(self, client):
        """Test that None response_format is valid."""
        # Should not raise an exception
        client.llm._validate_response_format(None)

    def test_json_object_format(self, client):
        """Test json_object response format validation."""
        response_format = {"type": "json_object"}
        # Should not raise an exception
        client.llm._validate_response_format(response_format)

    def test_json_schema_format(self, client):
        """Test json_schema response format validation."""
        response_format = {
            "type": "json_schema",
            "json_schema": {
                "name": "test_schema",
                "schema": {
                    "type": "object",
                    "properties": {"field": {"type": "string"}},
                },
            },
        }
        # Should not raise an exception
        client.llm._validate_response_format(response_format)

    def test_invalid_type_not_dict(self, client):
        """Test that non-dict response_format raises error."""
        from src.opengradient.client.exceptions import OpenGradientError

        with pytest.raises(OpenGradientError, match="response_format must be a dict"):
            client.llm._validate_response_format("invalid")

    def test_missing_type_field(self, client):
        """Test that missing 'type' field raises error."""
        from src.opengradient.client.exceptions import OpenGradientError

        with pytest.raises(OpenGradientError, match="response_format must have a 'type' field"):
            client.llm._validate_response_format({})

    def test_invalid_type_value(self, client):
        """Test that invalid type value raises error."""
        from src.opengradient.client.exceptions import OpenGradientError

        with pytest.raises(OpenGradientError, match="response_format type must be"):
            client.llm._validate_response_format({"type": "invalid_type"})

    def test_json_schema_missing_json_schema_field(self, client):
        """Test that json_schema type without json_schema field raises error."""
        from src.opengradient.client.exceptions import OpenGradientError

        with pytest.raises(OpenGradientError, match="must have a 'json_schema' field"):
            client.llm._validate_response_format({"type": "json_schema"})

    def test_json_schema_not_dict(self, client):
        """Test that non-dict json_schema raises error."""
        from src.opengradient.client.exceptions import OpenGradientError

        with pytest.raises(OpenGradientError, match="json_schema must be a dict"):
            client.llm._validate_response_format({"type": "json_schema", "json_schema": "invalid"})

    def test_json_schema_missing_name(self, client):
        """Test that json_schema without name raises error."""
        from src.opengradient.client.exceptions import OpenGradientError

        with pytest.raises(OpenGradientError, match="json_schema must have a 'name' field"):
            client.llm._validate_response_format({"type": "json_schema", "json_schema": {"schema": {}}})

    def test_json_schema_missing_schema(self, client):
        """Test that json_schema without schema raises error."""
        from src.opengradient.client.exceptions import OpenGradientError

        with pytest.raises(OpenGradientError, match="json_schema must have a 'schema' field"):
            client.llm._validate_response_format({"type": "json_schema", "json_schema": {"name": "test"}})


class TestStructuredOutputs:
    """Test structured output functionality with mocked backends."""

    @pytest.fixture
    def client(self, mock_web3, mock_abi_files):
        """Create a test client instance."""
        return Client(private_key="0x" + "1" * 64)

    @pytest.fixture
    def mock_x402_client(self):
        """Mock x402HttpxClient for testing."""
        with patch("src.opengradient.client.llm.x402HttpxClient") as mock_client_class:
            mock_client = MagicMock()
            mock_response = MagicMock()
            mock_response.headers = {}
            mock_client_class.return_value.__aenter__.return_value = mock_client
            yield mock_client, mock_response

    @pytest.fixture
    def mock_httpx_client(self):
        """Mock httpx.AsyncClient for streaming tests."""
        with patch("src.opengradient.client.llm.httpx.AsyncClient") as mock_client_class:
            mock_client = MagicMock()
            mock_client_class.return_value.__aenter__.return_value = mock_client
            yield mock_client

    def test_chat_with_json_object(self, client, mock_x402_client):
        """Test chat with json_object response format."""
        mock_client, mock_response = mock_x402_client
        mock_response.aread = MagicMock(
            return_value=json.dumps(
                {"choices": [{"message": {"role": "assistant", "content": '{"colors": ["red", "blue"]}'}, "finish_reason": "stop"}]}
            ).encode()
        )
        mock_client.post = MagicMock(return_value=mock_response)

        result = client.llm.chat(
            model=TEE_LLM.GPT_4O,
            messages=[{"role": "user", "content": "List colors"}],
            max_tokens=100,
            response_format={"type": "json_object"},
        )

        # Verify the call was made with response_format in payload
        call_kwargs = mock_client.post.call_args[1]
        assert "json" in call_kwargs
        assert call_kwargs["json"]["response_format"] == {"type": "json_object"}
        assert result.chat_output["content"] == '{"colors": ["red", "blue"]}'

    def test_chat_with_json_schema(self, client, mock_x402_client):
        """Test chat with json_schema response format."""
        mock_client, mock_response = mock_x402_client
        mock_response.aread = MagicMock(
            return_value=json.dumps(
                {"choices": [{"message": {"role": "assistant", "content": '{"count": 2}'}, "finish_reason": "stop"}]}
            ).encode()
        )
        mock_client.post = MagicMock(return_value=mock_response)

        schema = {"type": "object", "properties": {"count": {"type": "integer"}}}
        result = client.llm.chat(
            model=TEE_LLM.GPT_4O,
            messages=[{"role": "user", "content": "Count items"}],
            max_tokens=100,
            response_format={"type": "json_schema", "json_schema": {"name": "count", "schema": schema}},
        )

        # Verify the call was made with response_format in payload
        call_kwargs = mock_client.post.call_args[1]
        assert "response_format" in call_kwargs["json"]
        assert call_kwargs["json"]["response_format"]["type"] == "json_schema"
        assert result.chat_output["content"] == '{"count": 2}'

    def test_completion_with_response_format(self, client, mock_x402_client):
        """Test completion with response_format."""
        mock_client, mock_response = mock_x402_client
        mock_response.aread = MagicMock(return_value=json.dumps({"completion": '{"answer": 42}'}).encode())
        mock_client.post = MagicMock(return_value=mock_response)

        result = client.llm.completion(
            model=TEE_LLM.GPT_4O,
            prompt="Answer in JSON",
            max_tokens=100,
            response_format={"type": "json_object"},
        )

        # Verify the call was made with response_format in payload
        call_kwargs = mock_client.post.call_args[1]
        assert "response_format" in call_kwargs["json"]
        assert result.completion_output == '{"answer": 42}'

    def test_chat_without_response_format(self, client, mock_x402_client):
        """Test that chat works without response_format (backward compatibility)."""
        mock_client, mock_response = mock_x402_client
        mock_response.aread = MagicMock(
            return_value=json.dumps(
                {"choices": [{"message": {"role": "assistant", "content": "Hello"}, "finish_reason": "stop"}]}
            ).encode()
        )
        mock_client.post = MagicMock(return_value=mock_response)

        result = client.llm.chat(
            model=TEE_LLM.GPT_4O,
            messages=[{"role": "user", "content": "Hi"}],
            max_tokens=100,
        )

        # Verify response_format was not in the payload
        call_kwargs = mock_client.post.call_args[1]
        assert "response_format" not in call_kwargs["json"]
        assert result.chat_output["content"] == "Hello"
