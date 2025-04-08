# LibreChat Locally with Ollama

This guide demonstrates how to install LibreChat locally and integrate it with Ollama. You can chat and perform Retrieval-Augmented Generation (RAG) with any model using a web-based GUI.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configuration](#configuration)
- [Running the Application](#running-the-application)
- [Troubleshooting](#troubleshooting)
- [License](#license)

---

## Installation

1. **Create and Activate a Environment**

   ```bash

   ```


3. **Set Up Environment Variables**

   Copy the example environment file:

   ```bash
   cp .env.changed .env
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

## License

This project is licensed under the terms specified by the LibreChat project. For further details, see the [LibreChat License](https://librechat.ai).
