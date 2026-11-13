# Shadow IT Scanner — Angell Data Intelligence

Automated external attack surface discovery and executive risk profiling platform built for corporate security and IT governance teams.

## Overview

**Shadow IT Scanner** audits target domains to identify active web properties, evaluate digital footprint concentration, and generate board-ready **Executive Risk Profile** PDF briefings. Built by **Angell Data Intelligence**, the platform bridges low-level network discovery telemetry with high-contrast, automated executive reporting.

## Architecture & Tech Stack

- **Backend & API:** Python, Flask
- **Discovery & Analysis:** Custom Python reconnaissance engine, Kali Linux network utilities, Claude API (automated risk synthesis)
- **Document Generation:** ReportLab (dynamic UTC timestamped executive PDF generation)
- **Payments & Billing:** Stripe Checkout, Customer Portal, and Webhook event processing (`/stripe-webhook`)
- **Frontend Interface:** Retool (`https://angelldataintelligence--shadow-scanner.retool.app/`)
- **Hosting & Infrastructure:** Heroku (`https://angell-data-intelligence-76524b45f214.herokuapp.com/`)

## Key Features

- **Automated Target Domain Audits:** Real-time infrastructure reachability checks, active property mapping, and portfolio concentration analysis.
- **Executive Risk Profile Generation:** Automatically compiles scan findings into structured, client-ready PDF deliverables featuring portfolio snapshots, key findings, strategic governance recommendations, and scope disclaimers.
- **Subscription & Webhook Pipeline:** Cryptographically verified Stripe webhook handling (`checkout.session.completed`, `customer.subscription.updated`, `customer.subscription.deleted`) for real-time account gating.
- **Self-Serve Client Dashboard:** Retool-powered interface for executing scans, downloading executive reports, and managing active subscription tiers.

## Repository Structure

```text
shadow-it-scanner/
├── app.py                  # Main Flask application, API routes, and Stripe webhook listener
├── scanner/                # Domain discovery and infrastructure telemetry modules
├── reports/                # ReportLab PDF layout templates and executive briefing builders
├── retool/                 # Exported Retool frontend application snapshot (JSON)
├── requirements.txt        # Python dependencies
├── Procfile                # Heroku process configuration
└── README.md               # Project documentation
