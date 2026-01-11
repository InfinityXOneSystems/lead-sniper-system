#!/usr/bin/env python3
"""
LEAD SNIPER - AUTONOMOUS LEAD GENERATION SYSTEM
================================================
Main Entry Point | 110% Protocol | FAANG Enterprise-Grade

This is the main entry point for the Lead Sniper autonomous
lead generation system. It integrates all components:

- Manus Core (parallel processing, auto-heal)
- Vision Cortex (multi-perspective analysis)
- Vertex AI (Gemini + AutoML)
- Headless Scrapers (parallel instances)
- Hybrid Sync (local/cloud)
- Scheduled Execution (5 AM daily)

Usage:
    python main.py                    # Run pipeline once
    python main.py --schedule         # Run on schedule (5 AM daily)
    python main.py --daemon           # Run as background daemon
    python main.py --test             # Run in test mode
"""

import argparse
import asyncio
import json
import logging
import os
import sys
from datetime import datetime

# Add src to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from pipeline.autonomous_pipeline import (
    AutonomousPipeline,
    ScheduledPipelineRunner,
    PipelineConfig
)
from sync.hybrid_sync import HybridSyncManager, SyncConfig
from core.manus_core import ManusCore, SystemConfig

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s',
    handlers=[
        logging.StreamHandler(),
        logging.FileHandler('/home/ubuntu/lead-sniper/logs/lead_sniper.log')
    ]
)
logger = logging.getLogger('LeadSniper')


def print_banner():
    """Print system banner"""
    banner = """
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     ██╗     ███████╗ █████╗ ██████╗     ███████╗███╗   ██╗██╗██████╗ ███████╗██████╗  ║
║     ██║     ██╔════╝██╔══██╗██╔══██╗    ██╔════╝████╗  ██║██║██╔══██╗██╔════╝██╔══██╗ ║
║     ██║     █████╗  ███████║██║  ██║    ███████╗██╔██╗ ██║██║██████╔╝█████╗  ██████╔╝ ║
║     ██║     ██╔══╝  ██╔══██║██║  ██║    ╚════██║██║╚██╗██║██║██╔═══╝ ██╔══╝  ██╔══██╗ ║
║     ███████╗███████╗██║  ██║██████╔╝    ███████║██║ ╚████║██║██║     ███████╗██║  ██║ ║
║     ╚══════╝╚══════╝╚═╝  ╚═╝╚═════╝     ╚══════╝╚═╝  ╚═══╝╚═╝╚═╝     ╚══════╝╚═╝  ╚═╝ ║
║                                                                              ║
║     AUTONOMOUS LEAD GENERATION PIPELINE                                      ║
║     110% Protocol | FAANG Enterprise-Grade | Zero Human Hands                ║
║                                                                              ║
║     Powered by: Manus Core | Vision Cortex | Vertex AI | AutoML              ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
    """
    print(banner)


async def run_once(config: PipelineConfig):
    """Run pipeline once"""
    logger.info("Starting single pipeline run...")
    
    pipeline = AutonomousPipeline(config)
    result = await pipeline.run()
    
    print("\n" + "=" * 60)
    print("PIPELINE EXECUTION COMPLETE")
    print("=" * 60)
    print(f"Run ID: {result.run_id}")
    print(f"Stage: {result.stage.value}")
    print(f"Leads Scraped: {result.leads_scraped}")
    print(f"Leads Validated: {result.leads_validated}")
    print(f"Leads Analyzed: {result.leads_analyzed}")
    print(f"Leads Stored: {result.leads_stored}")
    print(f"Errors: {len(result.errors)}")
    if result.end_time and result.start_time:
        duration = (result.end_time - result.start_time).total_seconds()
        print(f"Duration: {duration:.1f} seconds")
    print("=" * 60)
    
    return result


async def run_scheduled(config: PipelineConfig):
    """Run pipeline on schedule"""
    logger.info("Starting scheduled pipeline runner...")
    
    runner = ScheduledPipelineRunner(config)
    await runner.start()


async def run_daemon(config: PipelineConfig):
    """Run as background daemon with hybrid sync"""
    logger.info("Starting daemon mode...")
    
    # Initialize sync manager
    sync_config = SyncConfig(
        local_primary=config.local_primary,
        cloud_fallback=True,
        sync_interval_seconds=60
    )
    sync_manager = HybridSyncManager(sync_config)
    await sync_manager.initialize()
    await sync_manager.start()
    
    # Start scheduled runner
    runner = ScheduledPipelineRunner(config)
    
    try:
        await runner.start()
    finally:
        await sync_manager.stop()


async def run_test(config: PipelineConfig):
    """Run in test mode with limited scope"""
    logger.info("Starting test mode...")
    
    # Reduce scope for testing
    config.max_parallel_scrapers = 5
    config.max_parallel_analysis = 5
    config.store_to_bigquery = False
    config.sync_to_firestore = False
    
    pipeline = AutonomousPipeline(config)
    result = await pipeline.run()
    
    print("\n" + "=" * 60)
    print("TEST RUN COMPLETE")
    print("=" * 60)
    print(f"Run ID: {result.run_id}")
    print(f"Leads Processed: {result.leads_stored}")
    print(f"Errors: {len(result.errors)}")
    print("=" * 60)
    
    return result


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description='Lead Sniper - Autonomous Lead Generation System'
    )
    parser.add_argument(
        '--schedule',
        action='store_true',
        help='Run on schedule (5 AM daily)'
    )
    parser.add_argument(
        '--daemon',
        action='store_true',
        help='Run as background daemon'
    )
    parser.add_argument(
        '--test',
        action='store_true',
        help='Run in test mode'
    )
    parser.add_argument(
        '--config',
        type=str,
        help='Path to config file'
    )
    parser.add_argument(
        '--schedule-time',
        type=str,
        default='05:00',
        help='Schedule time (HH:MM format, default: 05:00)'
    )
    parser.add_argument(
        '--max-scrapers',
        type=int,
        default=100,
        help='Maximum parallel scrapers (default: 100)'
    )
    parser.add_argument(
        '--local-primary',
        action='store_true',
        default=True,
        help='Use local as primary execution target'
    )
    
    args = parser.parse_args()
    
    # Print banner
    print_banner()
    
    # Create logs directory
    os.makedirs('/home/ubuntu/lead-sniper/logs', exist_ok=True)
    
    # Load or create config
    config = PipelineConfig(
        max_parallel_scrapers=args.max_scrapers,
        max_parallel_analysis=50,
        local_primary=args.local_primary,
        schedule_time=args.schedule_time,
        triple_check_enabled=True,
        store_to_bigquery=True,
        sync_to_firestore=True,
        save_to_local=True
    )
    
    if args.config and os.path.exists(args.config):
        with open(args.config) as f:
            config_data = json.load(f)
            for key, value in config_data.items():
                if hasattr(config, key):
                    setattr(config, key, value)
    
    # Run appropriate mode
    if args.schedule:
        asyncio.run(run_scheduled(config))
    elif args.daemon:
        asyncio.run(run_daemon(config))
    elif args.test:
        asyncio.run(run_test(config))
    else:
        asyncio.run(run_once(config))


if __name__ == '__main__':
    main()
