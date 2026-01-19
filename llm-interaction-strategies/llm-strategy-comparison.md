# LLM Interaction Strategy Comparison

A visual guide to the differences between 8 LLM providers for structured output generation.

---

## Visual Overview

### 1. Response Format Modes

```mermaid
flowchart TB
    subgraph Modes["Response Format Modes"]
        direction TB
        Text["Text Mode<br/>(Default)"]
        JSON["JSON Mode<br/>(json_object)"]
        Schema["JSON Schema Mode<br/>(Strict Enforcement)"]
    end

    subgraph TextProviders["Text Mode - All Providers"]
        direction LR
        T1["AI21"]
        T2["Anthropic"]
        T3["Cohere"]
        T4["DeepSeek"]
        T5["Google"]
        T6["Groq"]
        T7["Mistral"]
        T8["OpenAI"]
    end

    subgraph JSONProviders["JSON Object Mode"]
        direction LR
        J1["AI21 ✓"]
        J2["DeepSeek ✓"]
        J3["Groq ✓"]
        J4["Mistral ✓"]
        J5["OpenAI ✓"]
    end

    subgraph SchemaProviders["Schema Enforcement"]
        direction LR
        S1["Anthropic ✓"]
        S2["Cohere ✓"]
        S3["Google ✓"]
        S4["Groq ✓"]
        S5["Mistral ✓"]
        S6["OpenAI ✓"]
    end

    subgraph NoSchema["No Schema Support"]
        direction LR
        N1["AI21 ✗"]
        N2["DeepSeek ✗"]
    end

    Text --> TextProviders
    JSON --> JSONProviders
    Schema --> SchemaProviders
    Schema -.-> NoSchema

    style Schema fill:#4CAF50,color:#fff
    style JSON fill:#2196F3,color:#fff
    style Text fill:#9E9E9E,color:#fff
    style NoSchema fill:#f44336,color:#fff
```

### 2. Validation Pipeline

```mermaid
flowchart LR
    subgraph Input["API Call"]
        Prompt["Prompt + Schema"]
    end

    subgraph PreValidated["Pre-Validated Path"]
        direction TB
        PV1["Anthropic<br/>claude-sonnet-4-5"]
        PV2["OpenAI<br/>gpt-4o"]
        PyObj["Pydantic Object<br/>Direct from API"]
    end

    subgraph PostValidated["Post-Validated Path"]
        direction TB
        Others["AI21 | Cohere | DeepSeek<br/>Google | Groq | Mistral"]
        RawJSON["Raw JSON String"]
        Parse["json.loads()"]
        Validate["Pydantic<br/>Validation"]
    end

    subgraph Output["Result"]
        Final["Validated<br/>Structured Data"]
    end

    Prompt --> PV1 & PV2
    Prompt --> Others

    PV1 -->|".parsed_output"| PyObj
    PV2 -->|".parsed"| PyObj
    PyObj --> Final

    Others -->|".text / .content"| RawJSON
    RawJSON --> Parse
    Parse --> Validate
    Validate --> Final

    style PV1 fill:#4CAF50,color:#fff
    style PV2 fill:#4CAF50,color:#fff
    style PyObj fill:#81C784,color:#000
    style Others fill:#FF9800,color:#fff
    style RawJSON fill:#FFB74D,color:#000
    style Parse fill:#FFB74D,color:#000
    style Validate fill:#FFB74D,color:#000
```

---

## SDK Patterns

### 3. SDK Types and Response Access

```mermaid
flowchart TB
    subgraph SDKTypes["SDK Categories"]
        Native["Native SDKs<br/>(Provider-specific)"]
        Override["OpenAI SDK Override<br/>(base_url swap)"]
    end

    subgraph NativeList["Native SDK Providers"]
        ai21["ai21<br/>AI21Client()"]
        anthropic["anthropic<br/>Anthropic()"]
        cohere["cohere<br/>Client()"]
        google["google.genai<br/>Client()"]
        groq["groq<br/>Groq()"]
        mistral["mistralai<br/>Mistral()"]
        openai["openai<br/>OpenAI()"]
    end

    subgraph OverrideList["Override Pattern"]
        deepseek["openai + base_url<br/>api.deepseek.com"]
    end

    subgraph ResponsePatterns["Response Access Patterns"]
        parsed["Pre-parsed<br/>.parsed_output | .parsed"]
        choices["choices[0].message.content"]
        text[".text"]
    end

    Native --> ai21 & anthropic & cohere & google & groq & mistral & openai
    Override --> deepseek

    anthropic --> parsed
    openai --> parsed

    ai21 --> choices
    groq --> choices
    mistral --> choices
    deepseek --> choices

    cohere --> text
    google --> text

    style parsed fill:#4CAF50,color:#fff
    style choices fill:#2196F3,color:#fff
    style text fill:#9C27B0,color:#fff
    style deepseek fill:#FF9800,color:#fff
```

---

## Message Structure Patterns

### 4. Prompt Structure by Provider

```mermaid
flowchart TB
    subgraph Structures["Message Structures"]
        SysUser["System + User<br/>Messages"]
        UserOnly["User Message<br/>Only"]
        SingleContent["Single Content<br/>String"]
        ToolUse["Tool Calling<br/>Pattern"]
    end

    subgraph SysUserProviders["System + User"]
        SU1["Anthropic"]
        SU2["DeepSeek"]
        SU3["Groq"]
        SU4["OpenAI"]
    end

    subgraph UserOnlyProviders["User Only"]
        UO1["AI21"]
        UO2["Cohere"]
        UO3["Mistral"]
    end

    subgraph SingleProviders["Single Content"]
        SC1["Google Gemini"]
    end

    subgraph ToolProviders["Tool Calling"]
        TC1["Anthropic<br/>(Alternative)"]
    end

    SysUser --> SU1 & SU2 & SU3 & SU4
    UserOnly --> UO1 & UO2 & UO3
    SingleContent --> SC1
    ToolUse --> TC1

    style SysUser fill:#4CAF50,color:#fff
    style UserOnly fill:#2196F3,color:#fff
    style SingleContent fill:#FF9800,color:#fff
    style ToolUse fill:#9C27B0,color:#fff
```

---

## Schema Requirements Matrix

### 5. Special Requirements by Provider

```mermaid
flowchart TB
    subgraph Requirements["Schema Requirements"]
        direction TB

        subgraph DirectSchema["Direct Pydantic Support"]
            DS1["Anthropic ✓<br/>beta.messages.parse()"]
            DS2["OpenAI ✓<br/>beta.chat.completions.parse()"]
        end

        subgraph AdditionalProps["additionalProperties: false Required"]
            AP1["Groq ✓<br/>Recursive schema modification"]
            AP2["Mistral ✓<br/>Recursive schema modification"]
        end

        subgraph JSONExample["JSON Example in Prompt Required"]
            JE1["DeepSeek ⚠️<br/>Critical for output quality"]
        end

        subgraph NoEnforcement["No Schema Enforcement"]
            NE1["AI21<br/>Prompt-based only"]
        end
    end

    style DS1 fill:#4CAF50,color:#fff
    style DS2 fill:#4CAF50,color:#fff
    style AP1 fill:#2196F3,color:#fff
    style AP2 fill:#2196F3,color:#fff
    style JE1 fill:#FF9800,color:#fff
    style NE1 fill:#f44336,color:#fff
```

---

## Provider Characteristics

### 6. Speed, Cost, and Reliability

```mermaid
graph TB
    subgraph Speed["Inference Speed"]
        S1["🚀 Fastest<br/>Groq (LPU)"]
        S2["⚡ Fast<br/>Anthropic | OpenAI | Google"]
        S3["📊 Standard<br/>Others"]
    end

    subgraph Cost["Cost Efficiency"]
        C1["💰 Budget<br/>DeepSeek | Groq"]
        C2["💵 Mid-tier<br/>Mistral | Cohere | AI21"]
        C3["💎 Premium<br/>OpenAI | Anthropic"]
    end

    subgraph Reliability["Output Reliability"]
        R1["🏆 Highest<br/>Anthropic | OpenAI<br/>(Pre-validated)"]
        R2["✅ High<br/>Groq | Mistral | Google | Cohere<br/>(Schema enforced)"]
        R3["⚠️ Moderate<br/>DeepSeek | AI21<br/>(Manual validation)"]
    end

    style S1 fill:#4CAF50,color:#fff
    style S2 fill:#81C784,color:#000
    style C1 fill:#4CAF50,color:#fff
    style R1 fill:#4CAF50,color:#fff
    style R2 fill:#2196F3,color:#fff
    style R3 fill:#FF9800,color:#fff
```

---

## Quick Reference Tables

### Provider Comparison

| Provider | SDK | Model | Structured Output | Response Access | Key Feature |
|:---------|:----|:------|:------------------|:----------------|:------------|
| **AI21** | `ai21` native | `jamba-large` | `json_object` | `.choices[0].message.content` | Fixed 4096 tokens |
| **Anthropic** | `anthropic` native | `claude-sonnet-4-5` | `beta.messages.parse()` | `.parsed_output` | **Pre-validated Pydantic** |
| **Cohere** | `cohere` native | `command-a-03-2025` | `json_schema` | `.text` | Single message format |
| **DeepSeek** | OpenAI + base_url | `deepseek-chat` | `json_object` | `.choices[0].message.content` | **JSON example required** |
| **Google** | `google.genai` | `gemini-2.5-flash` | `response_json_schema` | `.text` | New unified SDK |
| **Groq** | `groq` native | `llama-4-scout-17b` | `json_schema` | `.choices[0].message.content` | **Fastest (LPU)** |
| **Mistral** | `mistralai` native | `mistral-small-latest` | `json_schema` | `.choices[0].message.content` | Uses `chat.complete()` |
| **OpenAI** | `openai` native | `gpt-4o` | `beta.chat.completions.parse()` | `.parsed` | **Pre-validated + refusal detection** |

### Schema Enforcement Levels

| Level | Providers | Description |
|:------|:----------|:------------|
| **🟢 Strict** | OpenAI, Anthropic | API guarantees schema compliance, returns Pydantic objects |
| **🔵 Enforced** | Cohere, Groq, Mistral, Google | API validates against schema |
| **🟡 JSON Only** | DeepSeek | Valid JSON guaranteed, schema not enforced |
| **🔴 None** | AI21 | Prompt-based guidance only |

### Retry Strategy

| Provider | Attempts | Wait Strategy | Common Issues |
|:---------|:---------|:--------------|:--------------|
| Most providers | 3 | Exponential backoff (4-60s) | Transient failures |
| **DeepSeek** | **5** | Exponential backoff | Empty responses |
| **Cohere** | 3 | **10+ seconds** | Rate limiting (429) |

---

## Response Access Code Patterns

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        Response Access Patterns                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  PRE-VALIDATED (No manual parsing needed)                               │
│  ─────────────────────────────────────────                              │
│  Anthropic:  response.parsed_output  ──▶  Pydantic Object               │
│  OpenAI:     message.parsed          ──▶  Pydantic Object               │
│                                                                         │
│  MANUAL PARSING REQUIRED                                                │
│  ──────────────────────────                                             │
│  AI21:       response.choices[0].message.content  ──▶  json.loads()    │
│  DeepSeek:   response.choices[0].message.content  ──▶  json.loads()    │
│  Groq:       response.choices[0].message.content  ──▶  json.loads()    │
│  Mistral:    response.choices[0].message.content  ──▶  json.loads()    │
│                                                                         │
│  TEXT ACCESS                                                            │
│  ───────────                                                            │
│  Cohere:     response.text  ──▶  json.loads()                          │
│  Google:     response.text  ──▶  json.loads()                          │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Decision Trees

### Choosing a Provider

```
                              ┌─────────────────────┐
                              │ Need Structured     │
                              │ Output from LLM?    │
                              └──────────┬──────────┘
                                         │
                    ┌────────────────────┼────────────────────┐
                    ▼                    ▼                    ▼
           ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
           │ Highest       │    │ Fastest       │    │ Most          │
           │ Reliability   │    │ Inference     │    │ Cost-Effective│
           └───────┬───────┘    └───────┬───────┘    └───────┬───────┘
                   │                    │                    │
                   ▼                    ▼                    ▼
           ┌───────────────┐    ┌───────────────┐    ┌───────────────┐
           │ Anthropic     │    │ Groq          │    │ DeepSeek      │
           │ OpenAI        │    │ (LPU Engine)  │    │ Groq          │
           └───────────────┘    └───────────────┘    └───────────────┘
```

### Validation Strategy

```
                              ┌─────────────────────┐
                              │ API Response        │
                              │ Received            │
                              └──────────┬──────────┘
                                         │
                    ┌────────────────────┴────────────────────┐
                    │                                         │
           ┌────────▼────────┐                       ┌────────▼────────┐
           │ Anthropic or    │                       │ Other Providers │
           │ OpenAI?         │                       │                 │
           └────────┬────────┘                       └────────┬────────┘
                    │                                         │
                    ▼                                         ▼
           ┌─────────────────┐                       ┌─────────────────┐
           │ Use .parsed_    │                       │ Extract from    │
           │ output or       │                       │ .text or        │
           │ .parsed         │                       │ .content        │
           └────────┬────────┘                       └────────┬────────┘
                    │                                         │
                    │                                         ▼
                    │                                ┌─────────────────┐
                    │                                │ json.loads()    │
                    │                                └────────┬────────┘
                    │                                         │
                    │                                         ▼
                    │                                ┌─────────────────┐
                    │                                │ Pydantic        │
                    │                                │ Validation      │
                    │                                └────────┬────────┘
                    │                                         │
                    └─────────────────┬───────────────────────┘
                                      │
                                      ▼
                              ┌───────────────┐
                              │ Validated     │
                              │ Data Object   │
                              └───────────────┘
```

---

## Critical Gotchas

### Provider-Specific Warnings

```
┌─────────────────────────────────────────────────────────────────────────┐
│                           ⚠️ CRITICAL WARNINGS                          │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  DeepSeek                                                               │
│  ─────────                                                              │
│  ⚠️ MUST include JSON example in prompt                                │
│  ⚠️ Only supports json_object mode (not json_schema)                   │
│  ⚠️ May return empty responses - use 5 retries                         │
│                                                                         │
│  Groq / Mistral                                                         │
│  ──────────────                                                         │
│  ⚠️ MUST add additionalProperties: false recursively to schema         │
│                                                                         │
│  Anthropic                                                              │
│  ─────────                                                              │
│  ⚠️ Requires beta header: structured-outputs-2025-11-13                │
│                                                                         │
│  Google Gemini                                                          │
│  ─────────────                                                          │
│  ⚠️ Doesn't support Pydantic gt/lt constraints in schema               │
│  ⚠️ Use ge/le (minimum/maximum) instead of gt/lt                       │
│                                                                         │
│  Cohere                                                                 │
│  ──────                                                                 │
│  ⚠️ May produce comma-separated numbers (3,796,742)                    │
│  ⚠️ May include markdown code blocks around JSON                       │
│  ⚠️ Needs JSON sanitization before parsing                             │
│                                                                         │
│  AI21                                                                   │
│  ────                                                                   │
│  ⚠️ No schema enforcement - must validate all output manually          │
│  ⚠️ Fixed 4096 max tokens limit                                        │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Model Self-Identification

### The Anti-Pattern

```
┌─────────────────────────────────────────────────────────────────────────┐
│                    ⛔ NEVER ASK LLMs TO SELF-IDENTIFY                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│  Problem: LLMs cannot reliably identify themselves                      │
│                                                                         │
│  Example: DeepSeek processing 10 countries                              │
│  ├── 5 countries: Identified as "DeepSeek" ✓                           │
│  └── 5 countries: Identified as "Google Gemini" ✗                      │
│                                                                         │
│  Why: Training data contains responses from multiple models             │
│                                                                         │
│  ──────────────────────────────────────────────────────────────         │
│                                                                         │
│  ❌ BAD: Ask the model                                                  │
│     response = client.chat("Who are you?")                             │
│     # May return wrong provider!                                        │
│                                                                         │
│  ✅ GOOD: Hardcode identity                                             │
│     return ModelIdentity(                                               │
│         model_provider="DeepSeek",  # From provider class              │
│         model_name=self.model       # "deepseek-chat"                  │
│     )                                                                   │
│                                                                         │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## API Key Environment Variables

| Provider | Environment Variable(s) |
|:---------|:------------------------|
| AI21 | `AI21_API_KEY` |
| Anthropic | `ANTHROPIC_API_KEY` |
| Cohere | `CO_API_KEY` or `COHERE_API_KEY` |
| DeepSeek | `DEEPSEEK_API_KEY` |
| Google | `GEMINI_API_KEY` or `GOOGLE_API_KEY` |
| Groq | `GROQ_API_KEY` |
| Mistral | `MISTRAL_API_KEY` |
| OpenAI | `OPENAI_API_KEY` |

---

## Summary: At a Glance

```
┌──────────────┬───────────┬───────────┬───────────┬───────────────────────┐
│   Provider   │  Schema   │   Speed   │   Cost    │    Best For           │
├──────────────┼───────────┼───────────┼───────────┼───────────────────────┤
│  Anthropic   │   🟢 ✓✓   │    ⚡     │    💎     │  Highest reliability  │
│  OpenAI      │   🟢 ✓✓   │    ⚡     │    💎     │  Refusal detection    │
│  Groq        │   🔵 ✓    │    🚀     │    💰     │  Speed + budget       │
│  Mistral     │   🔵 ✓    │    📊     │    💵     │  Good balance         │
│  Cohere      │   🔵 ✓    │    📊     │    💵     │  Schema support       │
│  Google      │   🔵 ✓    │    ⚡     │    💵     │  Gemini ecosystem     │
│  DeepSeek    │   🟡      │    📊     │    💰     │  Cost-effective       │
│  AI21        │   🔴      │    📊     │    💵     │  Jamba models         │
├──────────────┴───────────┴───────────┴───────────┴───────────────────────┤
│  Legend:  🟢 Pre-validated  🔵 Enforced  🟡 JSON only  🔴 None          │
│           🚀 Fastest  ⚡ Fast  📊 Standard                               │
│           💰 Budget  💵 Mid-tier  💎 Premium                            │
└──────────────────────────────────────────────────────────────────────────┘
```

---

*Last Updated: 2026-01-13*
