# LLM Interaction Nuances

This document captures the nuances, similarities, and differences in how various LLMs handle structured output interactions.

---

## Response Format Modes

### Overview

| LLM Provider | Text Mode | JSON Mode | JSON Schema Mode | Notes |
|--------------|-----------|-----------|------------------|-------|
| OpenAI | Default | `json_object` | `json_schema` | Full structured outputs with schema enforcement |
| DeepSeek | Default | `json_object` | Not supported | OpenAI-compatible API |
| Groq | Default | `json_object` | `json_schema` | Very fast inference, OpenAI-compatible SDK |
| Mistral | Default | `json_object` | Custom structured | Own SDK, JSON mode reliable |
| Cohere | Default | `json_object` | `json_object` + schema | Schema passed in `response_format.schema` |
| Anthropic | Default | Tool use | Tool use | Uses tool calling for structured output |
| AI21 | Default | JSON in prompt | Not supported | Schema guidance in prompt only |
| Google Gemini | Default | `application/json` | Schema supported | Uses `response_mime_type` parameter |

---

## DeepSeek

### Response Modes

**1. Text Mode (Default)**
```python
response_format={"type": "text"}
```
- Returns free-form text
- No structural constraints
- Default if `response_format` not specified

**2. JSON Mode**
```python
response_format={"type": "json_object"}
```
- Forces output to be valid JSON
- **Requirement**: Must include the word "json" somewhere in the prompt (system or user message)
- If "json" is missing from prompt, API returns an error

### Why the "json" Word Requirement?

This is a safety mechanism. The API wants explicit confirmation that you actually want JSON output, preventing accidental JSON mode activation.

```python
# This works:
messages=[{"role": "user", "content": "Return country data as json"}]

# This fails with an error:
messages=[{"role": "user", "content": "Return country data"}]
```

### JSON Schema Support

DeepSeek only supports basic `json_object` mode, not full JSON schema validation. Schema structure must be included in the prompt text - DeepSeek will follow it but doesn't enforce it at the API level.

### API Compatibility

DeepSeek API is **fully OpenAI-compatible**:
- Use OpenAI SDK with `base_url="https://api.deepseek.com"`
- Same request/response format as OpenAI
- Same `response_format` parameter

### Known Issues

- May occasionally return empty content (handle with retry logic)

---

## Groq

### Response Modes

**1. Text Mode (Default)**
```python
# No response_format specified
```

**2. JSON Mode**
```python
response_format={"type": "json_object"}
```
- Forces output to be valid JSON
- Groq's Python SDK mirrors OpenAI's API structure

**3. Structured Outputs (Strict Mode)**
```python
response_format={
    "type": "json_schema",
    "json_schema": {
        "name": "schema_name",
        "strict": True,
        "schema": {...}
    }
}
```
- Available on select models (GPT-OSS 20B/120B)
- Guarantees schema compliance via constrained decoding

### SDK Choice

Groq provides its own Python SDK (`groq`) which mirrors OpenAI's interface:

```python
from groq import Groq

client = Groq(api_key="...")
response = client.chat.completions.create(
    model="meta-llama/llama-4-scout-17b-16e-instruct",
    messages=[...],
    response_format={"type": "json_object"}
)
```

### Known Issues

- Streaming and tool use not supported with Structured Outputs
- Some models only support best-effort JSON mode (may need retry)
- Very fast inference (~10x faster than other providers)

### API Key Environment Variable

`GROQ_API_KEY`

---

## Mistral

### Response Modes

**1. Text Mode (Default)**
```python
# No response_format specified
```

**2. JSON Mode**
```python
response_format={"type": "json_object"}
```
- Forces output to be valid JSON
- Must explicitly ask for JSON in prompt for best results
- Output guaranteed to be valid JSON

### SDK Choice

Mistral provides its own Python SDK (`mistralai`):

```python
from mistralai import Mistral

client = Mistral(api_key="...")
response = client.chat.complete(  # Note: .complete() not .completions.create()
    model="mistral-large-latest",
    messages=[...],
    response_format={"type": "json_object"}
)
```

### SDK Method Difference

**IMPORTANT**: Mistral SDK uses `.chat.complete()` instead of `.chat.completions.create()` used by OpenAI/Groq.

### Known Issues

- None significant; JSON mode is reliable
- Recommend explicit JSON prompt for optimal results

### API Key Environment Variable

`MISTRAL_API_KEY`

---

## Cohere

### Response Modes

**1. Text Mode (Default)**
- Standard chat completion
- No structural constraints

**2. JSON Mode with Schema**
```python
response_format={
    "type": "json_object",
    "schema": {
        "type": "object",
        "properties": {...},
        "required": [...]
    }
}
```
- Full JSON schema validation
- Schema passed directly to API
- API enforces schema structure

### JSON Schema Support

Cohere supports **full JSON schema validation** via `response_format.schema` parameter. Unlike DeepSeek, Cohere validates the output against the schema at the API level.

### Known Issues

- May produce comma-separated numbers in JSON (e.g., `3,796,742` instead of `3796742`)
- May include markdown code blocks around JSON
- Rate limiting (429 errors) requires longer delays (~10 seconds)

### JSON Sanitization Required

Cohere responses may need sanitization for:
- Markdown code block markers
- Trailing commas
- Comma-separated numbers
- JavaScript-style comments
- Control characters

---

## OpenAI

### Response Modes

**1. Text Mode (Default)**
```python
# No response_format specified
```

**2. JSON Mode**
```python
response_format={"type": "json_object"}
```
- Ensures valid JSON output
- Must mention "json" in prompt

**3. JSON Schema Mode (Structured Outputs)**
```python
response_format={
    "type": "json_schema",
    "json_schema": {
        "name": "schema_name",
        "schema": {...}
    }
}
```
- Full schema enforcement at API level
- Guarantees output matches schema exactly
- Most robust structured output option

### Pydantic Integration

OpenAI SDK supports direct Pydantic model parsing:
```python
response = client.beta.chat.completions.parse(
    model="gpt-4o",
    messages=[...],
    response_format=PydanticModel
)
```

---

## Anthropic

### Response Modes

Anthropic uses **tool calling** for structured outputs rather than `response_format`:

```python
response = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    messages=[...],
    tools=[{
        "name": "get_country_info",
        "description": "...",
        "input_schema": {...}
    }]
)
```

### Key Differences

- No `response_format` parameter
- Schema defined via tool `input_schema`
- Response comes in `tool_use` content blocks
- More verbose but very reliable

---

## AI21 (Jamba)

### Response Modes

AI21's Jamba model does **not** support native JSON mode. Structured output is achieved through:

1. **Prompt Engineering**: Include schema in prompt
2. **JSON Extraction**: Parse JSON from text response
3. **Retry Logic**: Handle malformed JSON

### Example Prompt Strategy

```python
prompt = f"""Return information about {country} as a JSON object with these fields:
- description (string)
- population (integer)
...
Return ONLY the JSON, no other text."""
```

### Known Issues

- No guaranteed JSON structure
- May include explanatory text around JSON
- Requires robust JSON extraction and sanitization

---

## Google Gemini

### Response Modes

**1. Text Mode (Default)**

**2. JSON Mode**
```python
generation_config={
    "response_mime_type": "application/json",
    "response_schema": {...}  # Optional
}
```

### Schema Support

Gemini supports optional schema for JSON mode:
```python
generation_config={
    "response_mime_type": "application/json",
    "response_schema": {
        "type": "object",
        "properties": {...}
    }
}
```

### Known Issues

**Pydantic Schema Constraints Not Supported**

Google Gemini's `response_schema` only supports a **subset of JSON Schema**. Pydantic field constraints that generate certain JSON Schema properties will cause errors:

| Pydantic Constraint | JSON Schema Property | Gemini Support |
|---------------------|---------------------|----------------|
| `gt=0` | `exclusiveMinimum` | Not supported |
| `ge=0` | `minimum` | Supported |
| `lt=100` | `exclusiveMaximum` | Not supported |
| `le=100` | `maximum` | Supported |

**Example Error:**
```
4 validation errors for Schema
properties.area_sq_mile.exclusiveMinimum
  Extra inputs are not permitted [type=extra_forbidden, input_value=0, input_type=int]
```

**Workaround**: Don't pass Pydantic models with `gt`/`lt` constraints directly as `response_schema`. Instead:
1. Use `response_mime_type="application/json"` only (no schema)
2. Parse JSON response manually with `json.loads()`
3. Validate with Pydantic after receiving the response

```python
# Instead of this (fails with gt=0 constraints):
config=types.GenerateContentConfig(
    response_mime_type="application/json",
    response_schema=CountryInfo,  # Has gt=0 fields
)

# Do this:
config=types.GenerateContentConfig(
    response_mime_type="application/json",
    # No response_schema
)
# Then validate manually:
data = json.loads(response.text)
return CountryInfo(**data)  # Pydantic validates here
```

---

## Comparison Summary

### Schema Enforcement Level

| Provider | Enforcement | Notes |
|----------|-------------|-------|
| OpenAI (json_schema) | Strict | API guarantees schema compliance |
| Cohere | Strict | API validates against schema |
| Groq (json_schema) | Strict | Available on select models |
| Mistral | Moderate | JSON mode reliable, custom structured available |
| Google Gemini | Moderate | Schema supported but less strict |
| DeepSeek | None | JSON valid, but schema not enforced |
| AI21 | None | Prompt-based only |
| Anthropic | Moderate | Via tool calling |

### Ease of Implementation

| Provider | Complexity | Notes |
|----------|------------|-------|
| OpenAI | Low | Native Pydantic support |
| DeepSeek | Low | OpenAI-compatible |
| Groq | Low | Own SDK, OpenAI-compatible interface |
| Mistral | Low | Own SDK, simple JSON mode |
| Cohere | Medium | Good schema support, needs sanitization |
| Google Gemini | Medium | Different parameter names |
| Anthropic | Medium | Tool calling pattern |
| AI21 | High | Prompt engineering required |

### Robustness (JSON Parsing)

| Provider | Robustness | Common Issues |
|----------|------------|---------------|
| OpenAI | High | Rare issues |
| DeepSeek | Medium | Empty content occasionally |
| Groq | Medium | Very fast, occasional retry needed |
| Mistral | High | Rare issues, JSON mode reliable |
| Cohere | Medium | Comma-separated numbers, markdown |
| Google Gemini | Medium | Varies by model |
| Anthropic | High | Via tool use |
| AI21 | Low | Requires extensive sanitization |

---

## Best Practices

1. **Always implement retry logic** - All providers can have transient failures
2. **Sanitize JSON responses** - Even with JSON mode, LLMs may produce quirky JSON
3. **Include schema in prompt** - Even when API supports schema, prompt reinforcement helps
4. **Handle rate limits** - Implement exponential backoff (10+ seconds for 429 errors)
5. **Validate with Pydantic** - Use Pydantic models to validate parsed JSON
6. **Never ask LLMs to self-identify** - Use hardcoded model identity (see below)

---

## Model Self-Identification

### The Problem

LLMs **cannot reliably self-identify** when asked "Who are you?" or "What model is responding?". This is because:

1. **Training data contamination** - Models are trained on data containing responses from other models
2. **No true self-awareness** - LLMs generate text probabilistically, not from introspection
3. **Inconsistent responses** - The same model may identify differently across requests

### Real-World Example: DeepSeek

When processing 10 countries with DeepSeek, asking for model identity produced:
- 5 countries correctly identified as "DeepSeek"
- 5 countries **incorrectly** identified as "Google Gemini"

The 50/50 split indicates purely probabilistic behavior - DeepSeek's training data included Gemini responses.

### The Pattern: Hardcoded Identity

**Never** ask an LLM to self-identify. Instead, hardcode the model identity based on the provider configuration:

```python
# BAD - Unreliable
def get_model_identity(self) -> ModelIdentity:
    response = self.client.chat.completions.create(
        model=self.model,
        messages=[{
            "role": "user",
            "content": "Who is answering? Return as 'Provider: X | Model: Y'"
        }]
    )
    # Parse response... (may return wrong provider!)

# GOOD - Consistent and reliable
def get_model_identity(self) -> ModelIdentity:
    """Return hardcoded model identity.

    Note: LLMs cannot reliably self-identify as they may have been
    trained on data from other models. Using hardcoded values ensures
    consistency.
    """
    return ModelIdentity(
        model_provider="DeepSeek",  # Known from provider class
        model_name=self.model,       # "deepseek-chat"
    )
```

### Implementation Checklist

When implementing a new LLM provider:

- [ ] **DO** hardcode `model_provider` based on the provider class name
- [ ] **DO** use `self.model` (the configured model name) for `model_name`
- [ ] **DO NOT** make an API call to ask the model who it is
- [ ] **DO NOT** parse the model's response to extract identity

### Affected Providers (All Fixed)

| Provider | Hardcoded Values |
|----------|------------------|
| OpenAI | `"OpenAI"` / `self.model` |
| DeepSeek | `"DeepSeek"` / `self.model` |
| Groq | `"Groq"` / `self.model` |
| Mistral | `"Mistral"` / `self.model` |
| Google | `"Google"` / `self.model` |
| Anthropic | `"Anthropic"` / `self.model` |
| Cohere | `"Cohere"` / `self.model` |
| AI21 | `"AI21"` / `self.model` |

---

*Last Updated: 2026-01-05*
*Added: Mistral provider documentation*
*Added: Model Self-Identification pattern (hardcoded identity)*
*Added: Google Gemini Pydantic schema constraints gotcha*
