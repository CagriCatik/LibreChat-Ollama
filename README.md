# LibreChat Locally with Ollama

This guide demonstrates how to install LibreChat locally and integrate it with Ollama. You can chat and perform Retrieval-Augmented Generation (RAG) with any model (e.g., Llama 3, Mistral, Deepseek, etc.) using a web-based GUI.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
  - [LibreChat YAML Configuration](#librechat-yaml-configuration)
  - [Docker Compose Override](#docker-compose-override)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Prerequisites

Before you begin, ensure you have the following installed:

- [Conda](https://docs.conda.io/en/latest/)
- [Docker and Docker Compose](https://docs.docker.com/compose/install/)
- Git

---

## Installation

1. **Create and Activate a Conda Environment**

   ```bash
   conda create -n librechat python=3.11
   conda activate librechat
   ```

2. **Clone the LibreChat Repository**

   ```bash
   git clone https://github.com/danny-avila/LibreChat.git
   cd LibreChat
   ```

3. **Set Up Environment Variables**

   Copy the example environment file:

   ```bash
   cp .env.example .env
   ```

4. **Stop Any Existing Ollama Service**

   If you have an Ollama service running, stop it:

   ```bash
   sudo systemctl stop ollama.service
   ```

5. **Start LibreChat and Ollama via Docker**

   Bring up the containers in detached mode:

   ```bash
   docker compose up -d
   ```

6. **Verify the Running Services**

   Check the state of the containers:

   ```bash
   docker compose ps --format "{{.Service}} {{.State}}"
   ```

7. **Access the LibreChat Web Interface**

   Open your browser and navigate to:

   ```
   http://localhost:3080/
   ```

---

## Configuration

### LibreChat YAML Configuration

Create or update your **librechat.yaml** file with your custom endpoint configurations. This file defines the models and how LibreChat interacts with them.

Below is an example configuration that integrates the Ollama endpoint with models including Deepseek and Mistral:

```yaml
# For more information, see the Configuration Guide:
# https://www.librechat.ai/docs/configuration/librechat_yaml

version: 1.2.1
cache: true

interface:
  customWelcome: "Welcome to LibreChat! Enjoy your experience."
  privacyPolicy:
    externalUrl: 'https://librechat.ai/privacy-policy'
    openNewTab: true
  termsOfService:
    externalUrl: 'https://librechat.ai/tos'
    openNewTab: true
    modalAcceptance: true
    modalTitle: "Terms of Service for LibreChat"
    modalContent: |
      # Terms and Conditions for LibreChat

      *Effective Date: February 18, 2024*
      
      [Terms content truncated for brevity...]

  endpointsMenu: true
  modelSelect: true
  parameters: true
  sidePanel: true
  presets: true
  prompts: true
  bookmarks: true
  multiConvo: true
  agents: true

registration:
  socialLogins: ['github', 'google', 'discord', 'openid', 'facebook', 'apple']

actions:
  allowedDomains:
    - "swapi.dev"
    - "librechat.ai"
    - "google.com"

endpoints:
  custom:
    # Groq Example
    - name: 'groq'
      apiKey: '${GROQ_API_KEY}'
      baseURL: 'https://api.groq.com/openai/v1/'
      models:
        default:
          [
            'llama3-70b-8192',
            'llama3-8b-8192',
            'llama2-70b-4096',
            'mixtral-8x7b-32768',
            'gemma-7b-it',
          ]
        fetch: false
      titleConvo: true
      titleModel: 'mixtral-8x7b-32768'
      modelDisplayLabel: 'groq'

    # Mistral AI Example
    - name: 'Mistral'
      apiKey: '${MISTRAL_API_KEY}'
      baseURL: 'https://api.mistral.ai/v1'
      models:
        default: ['mistral-tiny', 'mistral-small', 'mistral-medium']
        fetch: true
      titleConvo: true
      titleModel: 'mistral-tiny'
      dropParams: ['stop', 'user', 'frequency_penalty', 'presence_penalty']

    # OpenRouter Example
    - name: 'OpenRouter'
      apiKey: '${OPENROUTER_KEY}'
      baseURL: 'https://openrouter.ai/api/v1'
      models:
        default: ['meta-llama/llama-3-70b-instruct']
        fetch: true
      titleConvo: true
      titleModel: 'meta-llama/llama-3-70b-instruct'
      dropParams: ['stop']
      modelDisplayLabel: 'OpenRouter'

    # Portkey AI Example
    - name: "Portkey"
      apiKey: "dummy"
      baseURL: 'https://api.portkey.ai/v1'
      headers:
          x-portkey-api-key: '${PORTKEY_API_KEY}'
          x-portkey-virtual-key: '${PORTKEY_OPENAI_VIRTUAL_KEY}'
      models:
          default: ['gpt-4o-mini', 'gpt-4o', 'chatgpt-4o-latest']
          fetch: true
      titleConvo: true
      titleModel: 'current_model'
      summarize: false
      summaryModel: 'current_model'
      forcePrompt: false
      modelDisplayLabel: 'Portkey'
      iconURL: https://images.crunchbase.com/image/upload/c_pad,f_auto,q_auto:eco,dpr_1/rjqy7ghvjoiu4cd1xjbf

    # Ollama Endpoint with Deepseek Models
    - name: "Ollama"
      apiKey: "ollama"
      # use 'host.docker.internal' if running LibreChat in a Docker container
      baseURL: "http://host.docker.internal:11434/v1/"
      models:
        default:
          - name: "deepseek-r1:14b"
            modelEndpoint: "/v1/models/deepseek-r1:14b"
            displayLabel: "Deepseek 14b"
            healthcheckEndpoint: "/v1/health"
          - name: "deepseek-r1:8b"
            modelEndpoint: "/v1/models/deepseek-r1:8b"
            displayLabel: "Deepseek 8b"
            healthcheckEndpoint: "/v1/health"
          - name: "mistral"
            modelEndpoint: "/v1/models/mistral"
            displayLabel: "Mistral"
            healthcheckEndpoint: "/v1/health"
        fetch: false
      titleConvo: true
      titleModel: "deepseek-r1:14b"
      summarize: false
      summaryModel: "mistral"
      forcePrompt: false
      modelDisplayLabel: "Ollama"
```

> **Note:**  
> Adjust the endpoints (`modelEndpoint`, `healthcheckEndpoint`) as needed based on your Ollama API and available models.

### Docker Compose Override

Create or update your **docker-compose-override.yaml** to ensure LibreChat uses your custom configuration file and to add the Ollama service:

```yaml
services:

  # USE LIBRECHAT CONFIG FILE
  api:
    volumes:
      - type: bind
        source: ./librechat.yaml
        target: /app/librechat.yaml

  # ADD OLLAMA SERVICE
  ollama:
    image: ollama/ollama:latest
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              capabilities: [compute, utility]
    ports:
      - "11500:11434"
    volumes:
      - ./ollama:/root/.ollama
```

> **Important:**  
> Update your **librechat.yaml** baseURL for Ollama to:
> 
> ```yaml
> baseURL: "http://host.docker.internal:11500/v1/"
> ```
> if you change the host port mapping.

---

## Running the Application

After completing the installation and configuration steps:

1. **Restart Docker Compose with Orphan Removal**

   ```bash
   docker compose down --remove-orphans
   docker compose up -d
   ```

2. **Verify Services are Running**

   ```bash
   docker compose ps --format "{{.Service}} {{.State}}"
   ```

3. **Access LibreChat**

   Open [http://localhost:3080/](http://localhost:3080/) in your browser.

---

## Troubleshooting

- **Port Binding Issues:**  
  If you encounter an error like "Ports are not available," ensure that no other process is using the designated host port (e.g., 11500). You can use commands like `netstat` to check for conflicts.

- **Configuration Not Loading:**  
  Double-check that the **librechat.yaml** file is correctly mounted into the Docker container. Also, verify the indentation and YAML syntax.

- **Service Health Checks:**  
  Use curl or your browser to verify that your Ollama health endpoint (e.g., `http://host.docker.internal:11500/v1/health`) is returning a valid response.

- **Browser Cache:**  
  Clear your browser cache or perform a hard refresh (Ctrl+F5 / Cmd+Shift+R) if changes are not reflected in the UI.

---

## License

This project is licensed under the terms specified by the LibreChat project. For further details, see the [LibreChat License](https://librechat.ai).
