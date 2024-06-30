# cvscore
Text Comparison API with LLM Integration
Overview:

This project develops an API that leverages various Large Language Models (LLM) such as OpenAI and Gemini to provide text comparison services. It supports authentication using JWT tokens and HMAC signatures, with the ability to manage API keys and user subscriptions effectively. This API is designed for developers and enterprises that require robust text analysis and comparison capabilities integrated with machine learning models.

Features:

Text Comparison: Allows users to upload reference texts and compare them with other texts, utilizing pre-configured LLM settings based on user-specific TypeIDs.
Dynamic API Key Management: Administrators can generate, assign, and revoke API keys linked with specific LLM configurations, ensuring controlled access to the API functions.
Subscription Management: Includes mechanisms to check subscription status and token availability, restricting access to API functions based on active subscriptions and token limits.
Support for Multiple File Formats: Accepts text input in various formats including Word, TXT, and PDF, enhancing flexibility for users.
Secure Access: Utilizes JWT for secure token-based authentication and HMAC for signature verification, ensuring secure API access.
Admin Interface: A comprehensive Django admin panel for managing TypeIDs, API keys, user subscriptions, and viewing logs.
Tech Stack:

Backend: Python, Django
Database: PostgreSQL
Authentication: JWT, HMAC
LLM Providers: OpenAI, Gemini
