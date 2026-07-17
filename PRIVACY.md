# Privacy Policy — EcoHash Model Provider Plugin

## What this plugin does

The EcoHash Model Provider plugin forwards your requests (prompts, messages, documents to
embed or rerank, and model parameters) from your Dify instance to the EcoHash inference
API at `https://api.ecohash.com`. It authenticates using the EcoHash API key you provide
in the provider settings.

## Data collected and processed

- **API key**: stored by Dify as a provider credential and sent to EcoHash as a
  `Bearer` token on each request. It is used only to authenticate and bill your requests.
  The plugin does not log the API key or transmit it anywhere other than the configured
  EcoHash endpoint.
- **Request content**: prompts, chat messages, and documents you submit are sent to
  EcoHash to generate completions, embeddings, or rerank results. This content is
  processed by EcoHash to serve the request.
- **No additional collection**: the plugin itself does not collect, store, or share any
  personal data beyond passing your request to EcoHash and returning the response. It does
  not use analytics or third-party trackers.

## Data handling by EcoHash

Content you send is processed by EcoHash to fulfill inference requests and for usage
metering/billing. Handling and retention are governed by EcoHash's own privacy policy and
terms:

- <https://ecohash.com/privacy>
- <https://ecohash.com/terms>

## Contact

For privacy questions about this plugin or the EcoHash platform, open an issue at
<https://github.com/ecohash-ai/ecohash-dify-plugin/issues> or see <https://docs.ecohash.com>.

*Last updated: 2026-07-17*
