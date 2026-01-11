#!/usr/bin/env python3
"""
SEED DATA LOADER
================
Loads and manages all seed data for the Lead Sniper crawlers.

Integrates:
- 100 seed URLs from federal/state data sources
- 100+ seed keywords with intent scoring
- 222 distressed property sources
- 68 property indicators
- Florida county targets

110% Protocol | FAANG Enterprise-Grade | Zero Human Hands
"""

import json
import logging
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s | %(name)s | %(levelname)s | %(message)s'
)
logger = logging.getLogger('SeedDataLoader')


class DataCategory(Enum):
    """Categories for seed data"""
    FEDERAL_SMB = "Federal SMB & Business Data"
    MACRO_RATES = "Macro & Rates Data"
    FEDERAL_PROCUREMENT = "Federal Procurement / Awards"
    STATE_BUSINESS = "State Business Registries"
    UCC_FILINGS = "UCC Filings"
    PERMITS_LICENSES = "Permits / Licenses"
    JOB_SIGNALS = "Job / Hiring Signals"
    NEWS_PRESS = "News / Press Releases"
    COMPANY_DATA = "Company Data"
    TRADE_GROUPS = "Trade Groups"
    DISTRESSED_PROPERTY = "Distressed Property"
    GOVERNMENT_AUCTION = "Government Auction"
    BANK_REO = "Bank REO"
    COURT_FILINGS = "Court Filings"


class IntentLevel(Enum):
    """Intent scoring levels"""
    HIGH = 5
    MEDIUM_HIGH = 4
    MEDIUM = 3
    MEDIUM_LOW = 2
    LOW = 1


@dataclass
class SeedURL:
    """Represents a seed URL for crawling"""
    url: str
    category: str
    priority: int = 1
    enabled: bool = True
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'url': self.url,
            'category': self.category,
            'priority': self.priority,
            'enabled': self.enabled
        }


@dataclass
class SeedKeyword:
    """Represents a seed keyword for search"""
    keyword: str
    category: str
    intent_score: int = 3
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'keyword': self.keyword,
            'category': self.category,
            'intent_score': self.intent_score
        }


@dataclass
class PropertyIndicator:
    """Represents a property distress indicator"""
    indicator: str
    category: str
    weight: float = 1.0
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'indicator': self.indicator,
            'category': self.category,
            'weight': self.weight
        }


class SeedDataLoader:
    """
    Loads and manages all seed data for Lead Sniper crawlers.
    
    Data sources:
    - config/consolidated_intelligence.json
    - config/treasure_coast_config.json
    """
    
    def __init__(self, config_dir: Optional[str] = None):
        if config_dir is None:
            # Default to the config directory relative to this file
            self.config_dir = Path(__file__).parent.parent.parent / 'config'
        else:
            self.config_dir = Path(config_dir)
        
        self._urls: List[SeedURL] = []
        self._keywords: List[SeedKeyword] = []
        self._indicators: List[PropertyIndicator] = []
        self._sources: List[Dict] = []
        self._loaded = False
    
    def load(self) -> bool:
        """Load all seed data from configuration files"""
        try:
            # Load consolidated intelligence
            intel_file = self.config_dir / 'consolidated_intelligence.json'
            if intel_file.exists():
                with open(intel_file, 'r') as f:
                    data = json.load(f)
                
                # Load URLs
                for url_data in data.get('seed_urls', []):
                    self._urls.append(SeedURL(
                        url=url_data.get('url', ''),
                        category=url_data.get('category', 'Unknown')
                    ))
                
                # Load keywords
                for kw_data in data.get('seed_keywords', []):
                    self._keywords.append(SeedKeyword(
                        keyword=kw_data.get('keyword', ''),
                        category=kw_data.get('category', 'Unknown'),
                        intent_score=kw_data.get('intent_score', 3)
                    ))
                
                # Load indicators
                for ind_data in data.get('indicators', []):
                    self._indicators.append(PropertyIndicator(
                        indicator=ind_data.get('indicator', ''),
                        category=ind_data.get('sheet', 'Unknown')
                    ))
                
                # Load sources
                self._sources = data.get('distressed_property_sources', [])
                
                logger.info(f"Loaded {len(self._urls)} URLs, {len(self._keywords)} keywords, "
                           f"{len(self._indicators)} indicators, {len(self._sources)} sources")
                self._loaded = True
                return True
            else:
                logger.warning(f"Config file not found: {intel_file}")
                return False
                
        except Exception as e:
            logger.error(f"Failed to load seed data: {e}")
            return False
    
    def get_urls(self, category: Optional[str] = None) -> List[SeedURL]:
        """Get seed URLs, optionally filtered by category"""
        if not self._loaded:
            self.load()
        
        if category:
            return [u for u in self._urls if category.lower() in u.category.lower()]
        return self._urls
    
    def get_keywords(self, min_intent: int = 1) -> List[SeedKeyword]:
        """Get seed keywords with minimum intent score"""
        if not self._loaded:
            self.load()
        
        return [k for k in self._keywords if k.intent_score >= min_intent]
    
    def get_high_intent_keywords(self) -> List[SeedKeyword]:
        """Get only high-intent keywords (score 4-5)"""
        return self.get_keywords(min_intent=4)
    
    def get_indicators(self) -> List[PropertyIndicator]:
        """Get all property indicators"""
        if not self._loaded:
            self.load()
        return self._indicators
    
    def get_sources(self, source_type: Optional[str] = None) -> List[Dict]:
        """Get distressed property sources"""
        if not self._loaded:
            self.load()
        
        if source_type:
            return [s for s in self._sources if s.get('type') == source_type]
        return self._sources
    
    def get_crawl_targets(self) -> List[str]:
        """Get all URLs suitable for crawling"""
        urls = self.get_urls()
        source_urls = [s['source'] for s in self.get_sources('url')]
        return [u.url for u in urls] + source_urls
    
    def get_search_terms(self) -> List[str]:
        """Get all keywords suitable for search"""
        keywords = self.get_keywords()
        source_keywords = [s['source'] for s in self.get_sources('keyword')]
        return [k.keyword for k in keywords] + source_keywords
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get statistics about loaded data"""
        if not self._loaded:
            self.load()
        
        return {
            'total_urls': len(self._urls),
            'total_keywords': len(self._keywords),
            'total_indicators': len(self._indicators),
            'total_sources': len(self._sources),
            'url_categories': list(set(u.category for u in self._urls)),
            'keyword_categories': list(set(k.category for k in self._keywords)),
            'high_intent_keywords': len(self.get_high_intent_keywords())
        }


# Pre-defined Treasure Coast targets
TREASURE_COAST_TARGETS = {
    "counties": [
        "St. Lucie",
        "Martin", 
        "Indian River",
        "Okeechobee"
    ],
    "zip_codes": [
        "34945", "34946", "34947", "34948", "34949", "34950",
        "34951", "34952", "34953", "34954", "34956", "34957",
        "34958", "34972", "34974", "34979", "34981", "34982",
        "34983", "34984", "34985", "34986", "34987", "34988",
        "34990", "34991", "34992", "34994", "34995", "34996",
        "34997", "32948", "32958", "32960", "32961", "32962",
        "32963", "32966", "32967", "32968", "32969", "32970",
        "32971", "32976", "32978"
    ],
    "cities": [
        "Fort Pierce", "Port St. Lucie", "Stuart", "Jensen Beach",
        "Vero Beach", "Sebastian", "Okeechobee", "Palm City",
        "Hobe Sound", "Indiantown"
    ]
}


# Pre-defined distressed property search terms
DISTRESSED_PROPERTY_TERMS = [
    "foreclosure",
    "pre-foreclosure",
    "bank owned",
    "REO",
    "short sale",
    "tax lien",
    "tax deed",
    "probate sale",
    "estate sale",
    "motivated seller",
    "as-is sale",
    "fixer upper",
    "handyman special",
    "distressed property",
    "auction property",
    "code violation",
    "vacant property",
    "abandoned property",
    "lis pendens",
    "notice of default"
]


def main():
    """Test the seed data loader"""
    loader = SeedDataLoader()
    
    if loader.load():
        stats = loader.get_statistics()
        print("\n=== SEED DATA STATISTICS ===")
        for key, value in stats.items():
            print(f"{key}: {value}")
        
        print("\n=== SAMPLE HIGH-INTENT KEYWORDS ===")
        for kw in loader.get_high_intent_keywords()[:10]:
            print(f"  [{kw.intent_score}] {kw.keyword} ({kw.category})")
        
        print("\n=== SAMPLE CRAWL TARGETS ===")
        for url in loader.get_crawl_targets()[:10]:
            print(f"  {url}")
    else:
        print("Failed to load seed data")


if __name__ == "__main__":
    main()
