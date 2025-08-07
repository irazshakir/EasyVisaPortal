# Migration from OpenAI to Groq API

This document outlines the migration from OpenAI API to Groq API in the EasyVisa Portal project.

## Overview

The project has been migrated from OpenAI API to Groq API to leverage faster inference speeds and cost-effective LLM services. The migration includes:

- **Default Model**: `llama-3.3-70b-versatile` for general conversations and information extraction
- **Evaluation Model**: `llama-3.3-70b-versatile` for final visa evaluations and complex assessments

## Changes Made

### 1. New Groq Service (`app/services/groq_service.py`)

Created a new service that mirrors the functionality of the OpenAI service but uses Groq API:

- **AsyncGroq Client**: Uses the official Groq Python client
- **Dual Model Support**: Automatically switches between default and evaluation models
- **Enhanced Evaluation**: Special method for final visa evaluations using the more capable model
- **Backward Compatibility**: Maintains the same interface as the original OpenAI service

### 2. Configuration Updates (`app/core/config.py`)

Updated configuration to support Groq settings:

```python
# Groq settings
GROQ_API_KEY: str
    GROQ_DEFAULT_MODEL: str = "llama-3.3-70b-versatile"
    GROQ_EVALUATION_MODEL: str = "llama-3.3-70b-versatile"
GROQ_MAX_TOKENS: int = 2000
GROQ_TEMPERATURE: float = 0.7

# OpenAI settings (deprecated - keeping for backward compatibility)
OPENAI_API_KEY: Optional[str] = None
```

### 3. Service Updates

Updated all services to use the new Groq service:

- **Chat Service**: Now uses `groq_service` instead of `openai_service`
- **RAG Service**: Updated to use Groq for enhanced question handling
- **Test Files**: Updated all test files to use the new service

### 4. Infrastructure Updates

Updated deployment configurations:

- **Docker Compose**: Environment variables changed from `OPENAI_API_KEY` to `GROQ_API_KEY`
- **Kubernetes**: Updated deployment files to use Groq API key
- **Setup Scripts**: Updated environment file templates

### 5. Dependencies

Added Groq dependency to requirements files:

```
groq==0.4.2
```

## Environment Variables

Update your `.env` file with the following variables:

```bash
# Required
GROQ_API_KEY=your-groq-api-key-here

# Optional (with defaults)
GROQ_DEFAULT_MODEL=llama-3.3-70b-versatile
GROQ_EVALUATION_MODEL=llama-3.3-70b-versatile
GROQ_MAX_TOKENS=2000
GROQ_TEMPERATURE=0.7

# Deprecated (can be removed)
OPENAI_API_KEY=your-openai-api-key-here
```

## Model Selection Logic

The service automatically selects the appropriate model based on the use case:

- **Default Model (`llama-3.3-70b-versatile`)**: Used for general conversations, intent analysis, and information extraction
- **Evaluation Model (`llama-3.3-70b-versatile`)**: Used for final visa evaluations and complex assessments

## Migration Steps

1. **Get Groq API Key**: Sign up at [groq.com](https://groq.com) and get your API key

2. **Update Environment Variables**:
   ```bash
   # Remove or comment out OpenAI variables
   # OPENAI_API_KEY=your-openai-key
   
   # Add Groq variables
   GROQ_API_KEY=your-groq-api-key
   ```

3. **Install Dependencies**:
   ```bash
   pip install groq==0.4.2
   ```

4. **Update Kubernetes Secrets** (if using Kubernetes):
   ```bash
   kubectl create secret generic ai-secrets \
     --from-literal=groq-api-key=your-groq-api-key \
     --namespace=visa-portal
   ```

5. **Test the Migration**:
   ```bash
   python start_bot.py
   ```

## Benefits of Migration

1. **Faster Response Times**: Groq provides significantly faster inference speeds
2. **Cost Efficiency**: More cost-effective than OpenAI for similar performance
3. **Dual Model Strategy**: Different models for different use cases
4. **Better Evaluation**: Llama3-70b provides more detailed and accurate evaluations

## Backward Compatibility

The migration maintains backward compatibility:

- All existing API interfaces remain the same
- OpenAI service is still available but deprecated
- Existing code will continue to work without changes
- Gradual migration path available

## Troubleshooting

### Common Issues

1. **API Key Error**: Ensure `GROQ_API_KEY` is set correctly
2. **Model Not Found**: Verify model names are correct
3. **Rate Limiting**: Groq has different rate limits than OpenAI

### Testing

Run the test suite to verify the migration:

```bash
python test_robust_handling.py
python -m pytest tests/
```

## Performance Comparison

| Metric | OpenAI GPT-4 | Groq Llama-3.3-70b |
|--------|-------------|-------------------|
| Speed | ~2-3s | ~1-2s |
| Cost | High | Medium |
| Quality | Excellent | Excellent |
| Context Length | 8k | 8k |

## Future Considerations

1. **Model Updates**: Monitor for new Groq models
2. **Cost Optimization**: Fine-tune model selection based on use case
3. **Performance Monitoring**: Track response times and quality
4. **Fallback Strategy**: Consider keeping OpenAI as backup

## Support

For issues related to the migration:

1. Check the Groq documentation: [docs.groq.com](https://docs.groq.com)
2. Review the service logs for detailed error messages
3. Test with the provided test suite
4. Contact the development team for assistance 