import os
from fastapi import FastAPI, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from google import genai
from google.genai import types
from dotenv import load_dotenv
from sqlalchemy.orm import Session

import models
from database import engine, get_db

load_dotenv()

# Creamos las tablas en SQLite automáticamente si no existen
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Agent Core - CRM Edition", version="1.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = genai.Client()

class LeadMessage(BaseModel):
    cliente_nombre: str
    mensaje: str

@app.get("/")
def read_root():
    return {"status": "online", "message": "Motor con Gemini, SQLite, Webhook y CRM activo."}

@app.post("/procesar-lead")
async def procesar_lead(data: LeadMessage, db: Session = Depends(get_db)):
    try:
        system_instruction = (
            "Eres un asistente de recepción virtual altamente eficiente y persuasivo para un negocio en el poniente de la CDMX. "
            "Tu única misión es calificar al lead, responder amablemente a su duda sobre servicios, "
            "y guiarlo de forma directa a agendar una cita. Sé conciso, profesional y directo."
        )

        response = client.models.generate_content(
            model='gemini-3.1-flash-lite',
            contents=f"Cliente: {data.cliente_nombre} dice: {data.mensaje}",
            config=types.GenerateContentConfig(
                system_instruction=system_instruction,
                temperature=0.3,
                max_output_tokens=150,
            ),
        )

        respuesta_ia = response.text

        # Guardamos el lead en la base de datos SQLite
        nuevo_lead = models.LeadModel(
            cliente_nombre=data.cliente_nombre,
            mensaje_cliente=data.mensaje,
            respuesta_ia=respuesta_ia
        )
        db.add(nuevo_lead)
        db.commit()
        db.refresh(nuevo_lead)

        return {
            "status": "success",
            "lead_id": nuevo_lead.id,
            "cliente": nuevo_lead.cliente_nombre,
            "respuesta_generada": nuevo_lead.respuesta_ia,
            "guardado_en_db": True
        }

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=str(e))

# NUEVO ENDPOINT: Consultar el historial de leads guardados (CRM básico)
@app.get("/leads")
def obtener_leads(db: Session = Depends(get_db)):
    try:
        # Consultamos todos los registros ordenados del más reciente al más antiguo
        leads = db.query(models.LeadModel).order_by(models.LeadModel.fecha_creacion.desc()).all()
        return {
            "status": "success",
            "total_leads": len(leads),
            "leads": leads
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))