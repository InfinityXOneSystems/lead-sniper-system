"""
VERTEX AI & AUTOML INTEGRATION
==============================
Google Cloud Vertex AI Flagship System Integration

Implements:
- Vertex AI Gemini for intelligent lead analysis
- AutoML for predictive lead scoring
- BigQuery integration for analytics
- Firestore for real-time data sync
"""

import asyncio
import json
import logging
import os
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Dict, List, Optional
from enum import Enum

logger = logging.getLogger('VertexAI')


class ModelType(Enum):
    """Vertex AI model types"""
    GEMINI_PRO = "gemini-2.5-flash"
    GEMINI_VISION = "gemini-pro-vision"
    AUTOML_TABULAR = "automl-tabular"
    AUTOML_TEXT = "automl-text"
    CUSTOM = "custom"


@dataclass
class VertexConfig:
    """Vertex AI configuration"""
    project_id: str = "infinity-x-one-systems"
    region: str = "us-central1"
    model_type: ModelType = ModelType.GEMINI_PRO
    enable_automl: bool = True
    enable_bigquery: bool = True
    enable_firestore: bool = True
    batch_size: int = 100
    max_concurrent_requests: int = 50


@dataclass
class PredictionResult:
    """Result from Vertex AI prediction"""
    input_id: str
    prediction: Any
    confidence: float
    model_version: str
    latency_ms: float
    timestamp: datetime = field(default_factory=datetime.utcnow)


class VertexAIClient:
    """
    Vertex AI Client for Lead Intelligence
    
    Provides AI-powered analysis and predictions for
    lead generation and scoring.
    """
    
    def __init__(self, config: Optional[VertexConfig] = None):
        self.config = config or VertexConfig()
        self._initialized = False
        self._client = None
        self._model = None
        logger.info(f"VertexAIClient initialized for project: {self.config.project_id}")
    
    async def initialize(self):
        """Initialize Vertex AI client"""
        try:
            # Try to import Google Cloud libraries
            from google.cloud import aiplatform
            from google.oauth2 import service_account
            
            # Check for service account key
            sa_key = os.environ.get('GCP_SA_KEY')
            if sa_key:
                # Parse service account key
                key_dict = json.loads(sa_key)
                credentials = service_account.Credentials.from_service_account_info(key_dict)
                
                aiplatform.init(
                    project=self.config.project_id,
                    location=self.config.region,
                    credentials=credentials
                )
            else:
                # Use default credentials
                aiplatform.init(
                    project=self.config.project_id,
                    location=self.config.region
                )
            
            self._initialized = True
            logger.info("Vertex AI client initialized successfully")
            
        except ImportError:
            logger.warning("Google Cloud AI Platform not available, using mock mode")
            self._initialized = True
        except Exception as e:
            logger.error(f"Vertex AI initialization error: {e}")
            self._initialized = True  # Continue in mock mode
    
    async def analyze_lead(self, lead_data: Dict) -> Dict:
        """
        Analyze a lead using Gemini AI
        
        Returns comprehensive analysis including:
        - Distress indicators
        - Opportunity score
        - Recommended actions
        - Risk assessment
        """
        try:
            if not self._initialized:
                await self.initialize()
            
            # Build analysis prompt
            prompt = self._build_analysis_prompt(lead_data)
            
            # Call Gemini API
            analysis = await self._call_gemini(prompt)
            
            return {
                'lead_id': lead_data.get('id'),
                'analysis': analysis,
                'distress_score': self._calculate_distress_score(lead_data),
                'opportunity_score': self._calculate_opportunity_score(lead_data),
                'recommended_actions': self._generate_recommendations(lead_data),
                'risk_level': self._assess_risk(lead_data),
                'timestamp': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Lead analysis error: {e}")
            return {
                'lead_id': lead_data.get('id'),
                'error': str(e),
                'timestamp': datetime.utcnow().isoformat()
            }
    
    def _build_analysis_prompt(self, lead_data: Dict) -> str:
        """Build prompt for Gemini analysis"""
        return f"""
        Analyze this distressed property lead for investment potential:
        
        Property Type: {lead_data.get('property_type', 'Unknown')}
        Address: {lead_data.get('address', 'Unknown')}
        List Price: ${lead_data.get('list_price', 0):,.0f}
        Estimated Value: ${lead_data.get('estimated_value', 0):,.0f}
        Profit Potential: ${lead_data.get('profit_potential', 0):,.0f}
        ROI: {lead_data.get('roi_percent', 0):.1f}%
        Data Source: {lead_data.get('data_source', 'Unknown')}
        Verification Status: {lead_data.get('verification_status', 'Unknown')}
        
        Provide:
        1. Investment viability assessment
        2. Key risk factors
        3. Recommended next steps
        4. Timeline urgency (1-10)
        5. Confidence level in data accuracy
        """
    
    async def _call_gemini(self, prompt: str) -> str:
        """Call Gemini API for analysis"""
        try:
            # Try using google-genai SDK
            import google.generativeai as genai
            
            api_key = os.environ.get('GEMINI_API_KEY')
            if api_key:
                genai.configure(api_key=api_key)
                model = genai.GenerativeModel(self.config.model_type.value)
                response = model.generate_content(prompt)
                return response.text
            else:
                return self._mock_analysis()
                
        except ImportError:
            return self._mock_analysis()
        except Exception as e:
            logger.error(f"Gemini API error: {e}")
            return self._mock_analysis()
    
    def _mock_analysis(self) -> str:
        """Mock analysis for testing"""
        return """
        Investment Analysis:
        - HIGH potential based on price-to-value ratio
        - Property shows strong distress indicators
        - Market conditions favorable for acquisition
        
        Risk Factors:
        - Verify title status before proceeding
        - Check for additional liens
        - Confirm property condition
        
        Recommended Actions:
        1. Conduct title search
        2. Schedule property inspection
        3. Prepare acquisition offer
        
        Timeline Urgency: 8/10
        Confidence Level: 85%
        """
    
    def _calculate_distress_score(self, lead_data: Dict) -> float:
        """Calculate distress score (0-100)"""
        score = 50.0
        
        property_type = lead_data.get('property_type', '')
        high_distress_types = ['foreclosure', 'tax_lien', 'bank_owned', 'auction']
        medium_distress_types = ['short_sale', 'probate', 'code_violation']
        
        if property_type in high_distress_types:
            score += 35
        elif property_type in medium_distress_types:
            score += 20
        
        # ROI factor
        roi = lead_data.get('roi_percent', 0)
        if roi > 100:
            score += 15
        elif roi > 50:
            score += 10
        
        return min(score, 100)
    
    def _calculate_opportunity_score(self, lead_data: Dict) -> float:
        """Calculate opportunity score (0-100)"""
        score = lead_data.get('opportunity_score', 50)
        
        # Adjust based on verification
        if lead_data.get('verification_status') == 'verified':
            score = min(score + 10, 100)
        
        # Adjust based on profit potential
        profit = lead_data.get('profit_potential', 0)
        if profit > 200000:
            score = min(score + 15, 100)
        elif profit > 100000:
            score = min(score + 10, 100)
        
        return score
    
    def _generate_recommendations(self, lead_data: Dict) -> List[str]:
        """Generate action recommendations"""
        recommendations = []
        
        property_type = lead_data.get('property_type', '')
        
        if property_type == 'auction':
            recommendations.append("Register for auction immediately")
            recommendations.append("Set maximum bid based on ARV analysis")
        elif property_type == 'foreclosure':
            recommendations.append("Contact lender for pre-foreclosure negotiation")
            recommendations.append("Prepare proof of funds")
        elif property_type == 'tax_lien':
            recommendations.append("Research redemption period")
            recommendations.append("Calculate total investment including back taxes")
        
        # Universal recommendations
        recommendations.append("Verify property title")
        recommendations.append("Conduct comparative market analysis")
        
        return recommendations
    
    def _assess_risk(self, lead_data: Dict) -> str:
        """Assess risk level"""
        verification = lead_data.get('verification_status', 'unverified')
        roi = lead_data.get('roi_percent', 0)
        
        if verification == 'verified' and roi > 30:
            return "LOW"
        elif verification == 'verified' or roi > 50:
            return "MEDIUM"
        else:
            return "HIGH"
    
    async def batch_analyze(self, leads: List[Dict]) -> List[Dict]:
        """Analyze multiple leads in parallel"""
        logger.info(f"Batch analyzing {len(leads)} leads")
        
        semaphore = asyncio.Semaphore(self.config.max_concurrent_requests)
        
        async def bounded_analyze(lead):
            async with semaphore:
                return await self.analyze_lead(lead)
        
        results = await asyncio.gather(
            *[bounded_analyze(lead) for lead in leads],
            return_exceptions=True
        )
        
        # Convert exceptions to error results
        final_results = []
        for i, result in enumerate(results):
            if isinstance(result, Exception):
                final_results.append({
                    'lead_id': leads[i].get('id'),
                    'error': str(result)
                })
            else:
                final_results.append(result)
        
        return final_results


class AutoMLPredictor:
    """
    AutoML Predictor for Lead Scoring
    
    Uses trained AutoML models for predictive
    lead scoring and prioritization.
    """
    
    def __init__(self, config: Optional[VertexConfig] = None):
        self.config = config or VertexConfig()
        self._model = None
        self._initialized = False
        logger.info("AutoMLPredictor initialized")
    
    async def initialize(self, model_name: str = "lead-scoring-model"):
        """Initialize AutoML model"""
        try:
            from google.cloud import aiplatform
            
            # Get model endpoint
            endpoints = aiplatform.Endpoint.list(
                filter=f'display_name="{model_name}"'
            )
            
            if endpoints:
                self._model = endpoints[0]
                self._initialized = True
                logger.info(f"AutoML model loaded: {model_name}")
            else:
                logger.warning(f"AutoML model not found: {model_name}")
                self._initialized = True  # Continue in mock mode
                
        except ImportError:
            logger.warning("AutoML not available, using rule-based scoring")
            self._initialized = True
    
    async def predict(self, features: Dict) -> PredictionResult:
        """Make a prediction using AutoML model"""
        start_time = datetime.utcnow()
        
        try:
            if self._model:
                # Use AutoML endpoint
                response = self._model.predict([features])
                prediction = response.predictions[0]
                confidence = float(prediction.get('confidence', 0.8))
            else:
                # Rule-based fallback
                prediction = self._rule_based_score(features)
                confidence = 0.75
            
            latency = (datetime.utcnow() - start_time).total_seconds() * 1000
            
            return PredictionResult(
                input_id=features.get('id', 'unknown'),
                prediction=prediction,
                confidence=confidence,
                model_version="v1.0" if self._model else "rule-based",
                latency_ms=latency
            )
            
        except Exception as e:
            logger.error(f"Prediction error: {e}")
            return PredictionResult(
                input_id=features.get('id', 'unknown'),
                prediction=self._rule_based_score(features),
                confidence=0.5,
                model_version="fallback",
                latency_ms=0
            )
    
    def _rule_based_score(self, features: Dict) -> float:
        """Rule-based scoring fallback"""
        score = 50.0
        
        # Property type scoring
        property_type = features.get('property_type', '')
        type_scores = {
            'foreclosure': 25,
            'auction': 20,
            'tax_lien': 20,
            'bank_owned': 15,
            'short_sale': 10,
            'probate': 10,
            'code_violation': 5
        }
        score += type_scores.get(property_type, 0)
        
        # ROI scoring
        roi = features.get('roi_percent', 0)
        if roi > 100:
            score += 20
        elif roi > 50:
            score += 10
        elif roi > 25:
            score += 5
        
        # Verification bonus
        if features.get('verification_status') == 'verified':
            score += 10
        
        return min(score, 100)
    
    async def batch_predict(self, features_list: List[Dict]) -> List[PredictionResult]:
        """Batch predictions"""
        results = await asyncio.gather(
            *[self.predict(f) for f in features_list]
        )
        return results


class BigQueryAnalytics:
    """
    BigQuery Analytics Integration
    
    Provides analytics and reporting capabilities
    for lead generation data.
    """
    
    def __init__(self, config: Optional[VertexConfig] = None):
        self.config = config or VertexConfig()
        self._client = None
        logger.info("BigQueryAnalytics initialized")
    
    async def initialize(self):
        """Initialize BigQuery client"""
        try:
            from google.cloud import bigquery
            
            sa_key = os.environ.get('GCP_SA_KEY')
            if sa_key:
                from google.oauth2 import service_account
                key_dict = json.loads(sa_key)
                credentials = service_account.Credentials.from_service_account_info(key_dict)
                self._client = bigquery.Client(
                    project=self.config.project_id,
                    credentials=credentials
                )
            else:
                self._client = bigquery.Client(project=self.config.project_id)
            
            logger.info("BigQuery client initialized")
            
        except ImportError:
            logger.warning("BigQuery not available")
        except Exception as e:
            logger.error(f"BigQuery initialization error: {e}")
    
    async def store_leads(self, leads: List[Dict], table_name: str = "leads"):
        """Store leads in BigQuery"""
        if not self._client:
            logger.warning("BigQuery not initialized, skipping storage")
            return
        
        try:
            table_id = f"{self.config.project_id}.lead_sniper.{table_name}"
            errors = self._client.insert_rows_json(table_id, leads)
            
            if errors:
                logger.error(f"BigQuery insert errors: {errors}")
            else:
                logger.info(f"Stored {len(leads)} leads in BigQuery")
                
        except Exception as e:
            logger.error(f"BigQuery storage error: {e}")
    
    async def query_leads(self, query: str) -> List[Dict]:
        """Query leads from BigQuery"""
        if not self._client:
            return []
        
        try:
            query_job = self._client.query(query)
            results = query_job.result()
            return [dict(row) for row in results]
        except Exception as e:
            logger.error(f"BigQuery query error: {e}")
            return []


class FirestoreSync:
    """
    Firestore Real-time Sync
    
    Provides real-time data synchronization
    for lead data across systems.
    """
    
    def __init__(self, config: Optional[VertexConfig] = None):
        self.config = config or VertexConfig()
        self._db = None
        logger.info("FirestoreSync initialized")
    
    async def initialize(self):
        """Initialize Firestore client"""
        try:
            from google.cloud import firestore
            
            sa_key = os.environ.get('GCP_SA_KEY')
            if sa_key:
                from google.oauth2 import service_account
                key_dict = json.loads(sa_key)
                credentials = service_account.Credentials.from_service_account_info(key_dict)
                self._db = firestore.Client(
                    project=self.config.project_id,
                    credentials=credentials
                )
            else:
                self._db = firestore.Client(project=self.config.project_id)
            
            logger.info("Firestore client initialized")
            
        except ImportError:
            logger.warning("Firestore not available")
        except Exception as e:
            logger.error(f"Firestore initialization error: {e}")
    
    async def sync_lead(self, lead: Dict):
        """Sync a single lead to Firestore"""
        if not self._db:
            return
        
        try:
            doc_ref = self._db.collection('leads').document(lead.get('id'))
            doc_ref.set(lead, merge=True)
            logger.debug(f"Synced lead {lead.get('id')} to Firestore")
        except Exception as e:
            logger.error(f"Firestore sync error: {e}")
    
    async def batch_sync(self, leads: List[Dict]):
        """Batch sync leads to Firestore"""
        if not self._db:
            return
        
        try:
            batch = self._db.batch()
            for lead in leads:
                doc_ref = self._db.collection('leads').document(lead.get('id'))
                batch.set(doc_ref, lead, merge=True)
            batch.commit()
            logger.info(f"Batch synced {len(leads)} leads to Firestore")
        except Exception as e:
            logger.error(f"Firestore batch sync error: {e}")
    
    def listen_for_changes(self, callback):
        """Listen for real-time changes"""
        if not self._db:
            return None
        
        def on_snapshot(doc_snapshot, changes, read_time):
            for change in changes:
                callback(change.type.name, change.document.to_dict())
        
        return self._db.collection('leads').on_snapshot(on_snapshot)


# Export classes
__all__ = [
    'VertexAIClient',
    'AutoMLPredictor',
    'BigQueryAnalytics',
    'FirestoreSync',
    'VertexConfig',
    'ModelType',
    'PredictionResult'
]
