# Lead Sniper 🎯

## Autonomous AI-Powered Lead Generation Pipeline

**110% Protocol | FAANG Enterprise-Grade | Zero Human Hands**

Lead Sniper is a fully autonomous lead generation system that combines the power of Manus Core parallel processing, Google Vertex AI, Vision Cortex multi-perspective analysis, and headless browser orchestration to generate high-quality distressed property leads 24/7.

---

## 🚀 Key Features

### Core Capabilities
- **Manus Core Engine**: Parallel MAP processing with auto-heal, auto-fix, and auto-optimize
- **Vision Cortex Integration**: Multi-perspective signal analysis for comprehensive lead scoring
- **Vertex AI + AutoML**: Gemini-powered analysis with predictive lead scoring
- **Headless Scraper Orchestration**: 100+ parallel browser instances for maximum throughput
- **Triple-Check Validation**: Three-stage validation ensuring 100% data accuracy
- **Hybrid Local/Cloud Sync**: Smart routing with automatic failover

### Autonomous Operation
- **Zero Human Intervention**: Fully autonomous E2E pipeline
- **Scheduled Execution**: Configurable daily runs (default: 5 AM)
- **Smart Routing**: Automatic local/cloud switching based on availability
- **Self-Healing**: Auto-recovery from failures and errors
- **Live Sync**: Real-time data synchronization across systems

---

## 📁 Repository Structure

```
lead-sniper/
├── src/
│   ├── core/
│   │   └── manus_core.py          # Core autonomous engine
│   ├── crawlers/                   # Web crawlers
│   ├── scrapers/
│   │   └── headless_orchestrator.py  # Parallel scraper system
│   ├── agents/                     # AI agents
│   ├── orchestrator/               # Task orchestration
│   ├── vertex_ai/
│   │   └── vertex_integration.py   # Vertex AI + AutoML
│   ├── vision_cortex/              # Multi-perspective analysis
│   ├── pipeline/
│   │   └── autonomous_pipeline.py  # Main pipeline
│   ├── validation/                 # Data validation
│   └── sync/
│       └── hybrid_sync.py          # Local/cloud sync
├── config/                         # Configuration files
├── results/
│   ├── raw/                        # Raw scraped data
│   ├── processed/                  # Processed leads
│   ├── leads/                      # Final lead outputs
│   └── reports/                    # Pipeline reports
├── scripts/                        # Utility scripts
├── tests/                          # Test suite
├── docs/                           # Documentation
├── infrastructure/
│   ├── docker/                     # Docker configs
│   ├── kubernetes/                 # K8s manifests
│   └── terraform/                  # IaC configs
├── frontend/                       # Web dashboard
├── backend/                        # API server
└── main.py                         # Main entry point
```

---

## 🛠 Installation

### Prerequisites
- Python 3.11+
- Node.js 18+
- Google Cloud SDK
- Docker (optional)

### Quick Start

```bash
# Clone repository
git clone https://github.com/InfinityXOneSystems/lead-sniper.git
cd lead-sniper

# Install dependencies
pip install -r requirements.txt

# Set environment variables
export GCP_SA_KEY='your-service-account-key'
export GEMINI_API_KEY='your-gemini-api-key'

# Run pipeline
python main.py
```

### Docker

```bash
# Build image
docker build -t lead-sniper .

# Run container
docker run -e GCP_SA_KEY=$GCP_SA_KEY lead-sniper
```

---

## 🚦 Usage

### Run Once
```bash
python main.py
```

### Scheduled Execution (5 AM Daily)
```bash
python main.py --schedule
```

### Daemon Mode (Background)
```bash
python main.py --daemon
```

### Test Mode
```bash
python main.py --test
```

### Custom Configuration
```bash
python main.py --config config/custom.json --max-scrapers 200 --schedule-time 06:00
```

---

## ⚙️ Configuration

### Pipeline Config
```python
PipelineConfig(
    max_parallel_scrapers=100,      # Parallel browser instances
    max_parallel_analysis=50,       # Concurrent AI analysis
    batch_size=100,                 # Processing batch size
    auto_start=True,                # Auto-start on init
    auto_heal=True,                 # Self-healing enabled
    auto_retry=True,                # Auto-retry on failure
    max_retries=3,                  # Maximum retry attempts
    local_primary=True,             # Local execution primary
    cloud_fallback=True,            # Cloud fallback enabled
    smart_routing=True,             # Smart routing enabled
    triple_check_enabled=True,      # Triple validation
    min_confidence_threshold=0.7,   # Minimum confidence
    store_to_bigquery=True,         # BigQuery storage
    sync_to_firestore=True,         # Firestore sync
    save_to_local=True,             # Local file storage
    scheduled_execution=True,       # Scheduled runs
    schedule_time="05:00"           # Daily run time
)
```

---

## 🔌 Integrations

### Google Cloud Platform
- **Vertex AI**: Gemini Pro for intelligent analysis
- **AutoML**: Predictive lead scoring models
- **BigQuery**: Analytics and reporting
- **Firestore**: Real-time data sync
- **Cloud Storage**: Data persistence
- **Cloud Run**: Serverless execution

### Data Sources
- Government foreclosure databases
- County clerk records
- Tax assessor data
- Auction platforms (Auction.com, etc.)
- Real estate platforms (Zillow, Redfin)
- Social media (Facebook Marketplace, etc.)

---

## 📊 Pipeline Stages

1. **Initialization**: Start all components
2. **Scraping**: Parallel headless scraping
3. **Validation**: Triple-check data validation
4. **Analysis**: Vision Cortex + Vertex AI
5. **Scoring**: AutoML prediction
6. **Enrichment**: Data enrichment
7. **Storage**: Multi-destination storage
8. **Reporting**: Generate reports

---

## 🎯 Lead Types

- Foreclosures
- Tax Liens
- Bank-Owned (REO)
- Short Sales
- Probate Properties
- Code Violations
- Auction Properties

---

## 📈 Metrics & Monitoring

The system tracks:
- Leads scraped/validated/analyzed/stored
- Execution time per stage
- Error rates and auto-heals
- Worker health and availability
- Sync status (local/cloud)

---

## 🔒 Security

- Service account authentication
- Encrypted credentials storage
- Stealth mode for scrapers
- Rate limiting and throttling
- Audit logging

---

## 📝 License

Proprietary - InfinityXOneSystems

---

## 🤝 Contributing

This is an internal system. Contact the development team for contribution guidelines.

---

## 📞 Support

For issues and support, contact the InfinityXOneSystems team.

---

**Built with ❤️ by InfinityXOneSystems**

*Powered by Manus Core | Vision Cortex | Vertex AI*
