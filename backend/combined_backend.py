'''
# Backend API Server - FastAPI backend with endpoints for lead CRUD, pipeline control, metrics, and WebSocket for real-time updates

# main.py
from fastapi import FastAPI, WebSocket, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List, Set
import asyncio

# database.py
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# models.py
from sqlalchemy import Column, Integer, String, Enum
import enum

# schemas.py
from pydantic import BaseModel
from typing import Optional


# database.py
SQLALCHEMY_DATABASE_URL = "sqlite:///./lead_sniper.db"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


# models.py
class LeadStatus(str, enum.Enum):
    new = "new"
    contacted = "contacted"
    qualified = "qualified"
    unqualified = "unqualified"

class Lead(Base):
    __tablename__ = "leads"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone_number = Column(String, index=True, nullable=True)
    company = Column(String, index=True, nullable=True)
    status = Column(Enum(LeadStatus), default=LeadStatus.new)


# schemas.py
class LeadBase(BaseModel):
    first_name: str
    last_name: str
    email: str
    phone_number: Optional[str] = None
    company: Optional[str] = None
    status: Optional[LeadStatus] = LeadStatus.new

class LeadCreate(LeadBase):
    pass

class LeadUpdate(LeadBase):
    pass

class Lead(LeadBase):
    id: int

    class Config:
        orm_mode = True


# crud.py
def get_lead(db: Session, lead_id: int):
    return db.query(Lead).filter(Lead.id == lead_id).first()

def get_leads(db: Session, skip: int = 0, limit: int = 100):
    return db.query(Lead).offset(skip).limit(limit).all()

def create_lead(db: Session, lead: LeadCreate):
    db_lead = Lead(**lead.dict())
    db.add(db_lead)
    db.commit()
    db.refresh(db_lead)
    return db_lead

def update_lead(db: Session, lead_id: int, lead: LeadUpdate):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead:
        for key, value in lead.dict(exclude_unset=True).items():
            setattr(db_lead, key, value)
        db.commit()
        db.refresh(db_lead)
    return db_lead

def delete_lead(db: Session, lead_id: int):
    db_lead = db.query(Lead).filter(Lead.id == lead_id).first()
    if db_lead:
        db.delete(db_lead)
        db.commit()
    return db_lead


# main.py
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

@app.post("/leads/", response_model=Lead)
def create_lead_api(lead: LeadCreate, db: Session = Depends(get_db)):
    return create_lead(db=db, lead=lead)

@app.get("/leads/", response_model=List[Lead])
def read_leads_api(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    leads = get_leads(db, skip=skip, limit=limit)
    return leads

@app.get("/leads/{lead_id}", response_model=Lead)
def read_lead_api(lead_id: int, db: Session = Depends(get_db)):
    db_lead = get_lead(db, lead_id=lead_id)
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

@app.put("/leads/{lead_id}", response_model=Lead)
def update_lead_api(lead_id: int, lead: LeadUpdate, db: Session = Depends(get_db)):
    db_lead = update_lead(db, lead_id=lead_id, lead=lead)
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

@app.delete("/leads/{lead_id}", response_model=Lead)
def delete_lead_api(lead_id: int, db: Session = Depends(get_db)):
    db_lead = delete_lead(db, lead_id=lead_id)
    if db_lead is None:
        raise HTTPException(status_code=404, detail="Lead not found")
    return db_lead

@app.post("/pipeline/control/")
async def pipeline_control():
    # Placeholder for pipeline control logic
    return {"message": "Pipeline control endpoint"}

@app.get("/metrics/")
async def get_metrics():
    # Placeholder for metrics logic
    return {"message": "Metrics endpoint"}

# WebSocket connections
connected_clients: Set[WebSocket] = set()

async def broadcast(message: str):
    for client in connected_clients:
        await client.send_text(message)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connected_clients.add(websocket)
    try:
        while True:
            data = await websocket.receive_text()
            await broadcast(f"Message from client: {data}")
    except Exception as e:
        print(f"WebSocket Error: {e}")
    finally:
        connected_clients.remove(websocket)
'''