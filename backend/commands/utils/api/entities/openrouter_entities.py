# Adapted from https://openrouter.ai/docs/api-reference/overview
#

from typing import Any, List, Literal, Union, Dict, Optional, TypedDict

# Definitions of subtypes are below

class TextContent(TypedDict):
    type: Literal['text']
    text: str


class ImageURL(TypedDict):
    url: str  # URL or base64 encoded image data
    detail: Optional[str]  # Optional, defaults to "auto"

class ImageContentPart(TypedDict):
    type: Literal['image_url']
    image_url: ImageURL

ContentPart = Union[TextContent, ImageContentPart]

class UserAssistantSystemMessage(TypedDict):
    role: Literal['user', 'assistant', 'system']
    # ContentParts are only for the "user" role:
    content: Union[str, List[ContentPart]]
    # If "name" is included, it will be prepended like this
    # for non-OpenAI models: `{name}: {content}`
    name: Optional[str]

class ToolMessage(TypedDict):
    role: Literal['tool']
    content: str
    tool_call_id: str
    name: Optional[str]

OpenRouterMessage = Union[UserAssistantSystemMessage, ToolMessage]
# OpenRouterMessage = UserAssistantSystemMessage

class FunctionDescription(TypedDict):
    description: Optional[str]
    name: str
    parameters: object  # JSON Schema object

class Tool(TypedDict):
    type: Literal['function']
    function: FunctionDescription

ToolChoice = Union[Literal['none', 'auto'], Tool]

class Prediction(TypedDict):
    type: Literal['content']
    content: str

OpenRouterResponseFormat = Optional[Dict[str, str]]

class OpenRouterRequest(TypedDict):
    # Either "messages" or "prompt" is required
    messages: Optional[List[OpenRouterMessage]]
    prompt: Optional[str]

    # If "model" is unspecified, uses the user's default
    model: Optional[str]

    # Allows to force the model to produce specific output format.
    # See models page and note on this docs page for which models support it.
    response_format: OpenRouterResponseFormat  # Assuming { type: 'json_object' } is represented as {'type': 'json_object'}

    stop: Optional[Union[str, List[str]]]
    stream: Optional[bool] # Enable streaming

    # See LLM Parameters (openrouter.ai/docs/api-reference/parameters)
    max_tokens: Optional[int] # Range: [1, context_length)
    temperature: Optional[float] # Range: [0, 2]

    # Tool calling
    # Will be passed down as-is for providers implementing OpenAI's interface.
    # For providers with custom interfaces, we transform and map the properties.
    # Otherwise, we transform the tools into a YAML template. The model responds with an assistant message.
    # See models supporting tool calling: openrouter.ai/models?supported_parameters=tools
    tools: Optional[List[Tool]]
    tool_choice: Optional[ToolChoice]

    # Advanced optional parameters
    seed: Optional[int] # Integer only
    top_p: Optional[float] # Range: (0, 1]
    top_k: Optional[int] # Range: [1, Infinity) Not available for OpenAI models
    frequency_penalty: Optional[float] # Range: [-2, 2]
    presence_penalty: Optional[float] # Range: [-2, 2]
    repetition_penalty: Optional[float] # Range: (0, 2]
    logit_bias: Optional[Dict[int, float]]
    top_logprobs: Optional[int] # Integer only
    min_p: Optional[float] # Range: [0, 1]
    top_a: Optional[float] # Range: [0, 1]

    # Reduce latency by providing the model with a predicted output
    # https://platform.openai.com/docs/guides/latency-optimization#use-predicted-outputs
    prediction: Prediction

    # OpenRouter-only parameters
    # See "Prompt Transforms" section: openrouter.ai/docs/transforms
    transforms: Optional[List[str]]
    # See "Model Routing" section: openrouter.ai/docs/model-routing
    models: Optional[List[str]]
    route: Literal['fallback']
    # See "Provider Routing" section: openrouter.ai/docs/provider-routing
    provider: Optional[Any]

class ErrorResponse(TypedDict):
    code: int # See "Error Handling" section
    message: str
    metadata: Optional[Dict[str, Any]] # Contains additional error information such as provider details, the raw error message, etc.

class ToolCall(TypedDict):
    id: str
    type: Literal['function']
    function: FunctionDescription

class NonChatChoice(TypedDict):
    finish_reason: Optional[str]
    text: str
    error: Optional[ErrorResponse]

class NonStreamingChoiceMessage(TypedDict):
    content: Optional[str]
    role: str
    tool_calls: Optional[List[ToolCall]]

class NonStreamingChoice(TypedDict):
    finish_reason: Optional[str]
    native_finish_reason: Optional[str]
    message: NonStreamingChoiceMessage
    error: Optional[ErrorResponse]

class StreamingChoice(TypedDict):
    finish_reason: Optional[str]
    native_finish_reason: Optional[str]
    delta: NonStreamingChoiceMessage
    error: Optional[ErrorResponse]


# If the provider returns usage, we pass it down
# as-is. Otherwise, we count using the GPT-4 tokenizer.
class ResponseUsage(TypedDict):
    # Including images and tools if any
    prompt_tokens: int
    # The tokens generated
    completion_tokens: int
    # Sum of the above two fields
    total_tokens: int

class OpenRouterResponse(TypedDict):
    id: str
    # Depending on whether you set "stream" to "true" and
    # whether you passed in "messages" or a "prompt", you
    # will get a different output shape
    choices: List[Union[NonStreamingChoice, StreamingChoice, NonChatChoice]]
    created: int # Unix timestamp
    model: str
    object: Literal['chat.completion', 'chat.completion.chunk']

    system_fingerprint: Optional[str] # Only present if the provider supports it

    # Usage data is always returned for non-streaming.
    # When streaming, you will get one usage object at
    # the end accompanied by an empty choices array.
    usage: Optional[ResponseUsage]
