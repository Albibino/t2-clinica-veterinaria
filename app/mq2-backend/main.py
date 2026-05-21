import os
import uuid
import shutil
from datetime import datetime, timedelta
from typing import Optional, List
from pathlib import Path
from fastapi import FastAPI, Depends, HTTPException, status, UploadFile, File, Form
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from fastapi.staticfiles import StaticFiles
from jose import JWTError, jwt
from passlib.context import CryptContext
from sqlalchemy.orm import Session
from pydantic import BaseModel
from database import get_db, engine
import models

SECRET_KEY = os.getenv("SECRET_KEY", "super-secret-jwt-key-clinica-vet-2026")
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 480  # 8 horas

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

UPLOAD_DIR = Path("/app/uploads/fotos")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

models.Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Clínica Veterinária API",
    description="API para gerenciamento da clínica veterinária",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.mount("/uploads", StaticFiles(directory="/app/uploads"), name="uploads")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


class Token(BaseModel):
    access_token: str
    token_type: str
    username: str

class AnimalCreate(BaseModel):
    nome: str
    especie: str
    raca: Optional[str] = None
    idade: Optional[int] = None
    peso: Optional[float] = None
    nome_dono: str
    contato_dono: Optional[str] = None
    observacoes: Optional[str] = None

class AnimalUpdate(BaseModel):
    nome: Optional[str] = None
    especie: Optional[str] = None
    raca: Optional[str] = None
    idade: Optional[int] = None
    peso: Optional[float] = None
    nome_dono: Optional[str] = None
    contato_dono: Optional[str] = None
    observacoes: Optional[str] = None

class AnimalResponse(BaseModel):
    id: int
    nome: str
    especie: str
    raca: Optional[str]
    idade: Optional[int]
    peso: Optional[float]
    nome_dono: str
    contato_dono: Optional[str]
    foto_url: Optional[str]
    observacoes: Optional[str]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class ConsultaCreate(BaseModel):
    animal_id: int
    data_consulta: datetime
    veterinario: str
    motivo: str
    diagnostico: Optional[str] = None
    tratamento: Optional[str] = None
    medicamentos: Optional[str] = None
    peso_consulta: Optional[float] = None
    retorno: Optional[str] = None
    status: Optional[str] = "agendada"
    observacoes: Optional[str] = None

class ConsultaUpdate(BaseModel):
    data_consulta: Optional[datetime] = None
    veterinario: Optional[str] = None
    motivo: Optional[str] = None
    diagnostico: Optional[str] = None
    tratamento: Optional[str] = None
    medicamentos: Optional[str] = None
    peso_consulta: Optional[float] = None
    retorno: Optional[str] = None
    status: Optional[str] = None
    observacoes: Optional[str] = None

class ConsultaResponse(BaseModel):
    id: int
    animal_id: int
    animal_nome: Optional[str] = None
    animal_especie: Optional[str] = None
    data_consulta: datetime
    veterinario: str
    motivo: str
    diagnostico: Optional[str]
    tratamento: Optional[str]
    medicamentos: Optional[str]
    peso_consulta: Optional[float]
    retorno: Optional[str]
    status: str
    observacoes: Optional[str]
    created_at: datetime

    class Config:
        from_attributes = True

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

async def get_current_user(token: str = Depends(oauth2_scheme)):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Token inválido ou expirado",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
    except JWTError:
        raise credentials_exception
    return username

@app.post("/api/auth/login", response_model=Token, tags=["Autenticação"])
async def login(form_data: OAuth2PasswordRequestForm = Depends()):
    if form_data.username != ADMIN_USERNAME or form_data.password != ADMIN_PASSWORD:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(
        data={"sub": form_data.username},
        expires_delta=timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    return {"access_token": access_token, "token_type": "bearer", "username": form_data.username}

@app.get("/api/auth/verify", tags=["Autenticação"])
async def verify_token(current_user: str = Depends(get_current_user)):
    return {"valid": True, "username": current_user}

@app.get("/api/animais", response_model=List[AnimalResponse], tags=["Animais"])
async def listar_animais(
    search: Optional[str] = None,
    especie: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    query = db.query(models.Animal)
    if search:
        query = query.filter(
            models.Animal.nome.ilike(f"%{search}%") |
            models.Animal.nome_dono.ilike(f"%{search}%")
        )
    if especie:
        query = query.filter(models.Animal.especie.ilike(f"%{especie}%"))
    return query.order_by(models.Animal.nome).all()

@app.get("/api/animais/{animal_id}", response_model=AnimalResponse, tags=["Animais"])
async def buscar_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    return animal

@app.post("/api/animais", response_model=AnimalResponse, status_code=201, tags=["Animais"])
async def criar_animal(
    nome: str = Form(...),
    especie: str = Form(...),
    raca: Optional[str] = Form(None),
    idade: Optional[int] = Form(None),
    peso: Optional[float] = Form(None),
    nome_dono: str = Form(...),
    contato_dono: Optional[str] = Form(None),
    observacoes: Optional[str] = Form(None),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    foto_url = None
    if foto and foto.filename:
        ext = Path(foto.filename).suffix.lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            raise HTTPException(status_code=400, detail="Formato de imagem inválido")
        filename = f"{uuid.uuid4()}{ext}"
        filepath = UPLOAD_DIR / filename
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        foto_url = f"/uploads/fotos/{filename}"

    animal = models.Animal(
        nome=nome, especie=especie, raca=raca, idade=idade,
        peso=peso, nome_dono=nome_dono, contato_dono=contato_dono,
        foto_url=foto_url, observacoes=observacoes
    )
    db.add(animal)
    db.commit()
    db.refresh(animal)
    return animal

@app.put("/api/animais/{animal_id}", response_model=AnimalResponse, tags=["Animais"])
async def atualizar_animal(
    animal_id: int,
    nome: Optional[str] = Form(None),
    especie: Optional[str] = Form(None),
    raca: Optional[str] = Form(None),
    idade: Optional[int] = Form(None),
    peso: Optional[float] = Form(None),
    nome_dono: Optional[str] = Form(None),
    contato_dono: Optional[str] = Form(None),
    observacoes: Optional[str] = Form(None),
    foto: Optional[UploadFile] = File(None),
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")

    if foto and foto.filename:
        ext = Path(foto.filename).suffix.lower()
        if ext not in ['.jpg', '.jpeg', '.png', '.gif', '.webp']:
            raise HTTPException(status_code=400, detail="Formato de imagem inválido")
        # Remove foto antiga
        if animal.foto_url:
            old_path = Path("/app") / animal.foto_url.lstrip("/")
            if old_path.exists():
                old_path.unlink()
        filename = f"{uuid.uuid4()}{ext}"
        filepath = UPLOAD_DIR / filename
        with open(filepath, "wb") as buffer:
            shutil.copyfileobj(foto.file, buffer)
        animal.foto_url = f"/uploads/fotos/{filename}"

    if nome is not None: animal.nome = nome
    if especie is not None: animal.especie = especie
    if raca is not None: animal.raca = raca
    if idade is not None: animal.idade = idade
    if peso is not None: animal.peso = peso
    if nome_dono is not None: animal.nome_dono = nome_dono
    if contato_dono is not None: animal.contato_dono = contato_dono
    if observacoes is not None: animal.observacoes = observacoes

    db.commit()
    db.refresh(animal)
    return animal

@app.delete("/api/animais/{animal_id}", tags=["Animais"])
async def deletar_animal(
    animal_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    animal = db.query(models.Animal).filter(models.Animal.id == animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")
    if animal.foto_url:
        old_path = Path("/app") / animal.foto_url.lstrip("/")
        if old_path.exists():
            old_path.unlink()
    db.delete(animal)
    db.commit()
    return {"message": f"Animal '{animal.nome}' removido com sucesso"}

@app.get("/api/consultas", tags=["Consultas"])
async def listar_consultas(
    animal_id: Optional[int] = None,
    status_filter: Optional[str] = None,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    query = db.query(models.Consulta, models.Animal).join(
        models.Animal, models.Consulta.animal_id == models.Animal.id
    )
    if animal_id:
        query = query.filter(models.Consulta.animal_id == animal_id)
    if status_filter:
        query = query.filter(models.Consulta.status == status_filter)

    results = query.order_by(models.Consulta.data_consulta.desc()).all()

    consultas = []
    for consulta, animal in results:
        c = {
            "id": consulta.id,
            "animal_id": consulta.animal_id,
            "animal_nome": animal.nome,
            "animal_especie": animal.especie,
            "animal_foto": animal.foto_url,
            "data_consulta": consulta.data_consulta.isoformat(),
            "veterinario": consulta.veterinario,
            "motivo": consulta.motivo,
            "diagnostico": consulta.diagnostico,
            "tratamento": consulta.tratamento,
            "medicamentos": consulta.medicamentos,
            "peso_consulta": float(consulta.peso_consulta) if consulta.peso_consulta else None,
            "retorno": str(consulta.retorno) if consulta.retorno else None,
            "status": consulta.status,
            "observacoes": consulta.observacoes,
            "created_at": consulta.created_at.isoformat(),
        }
        consultas.append(c)
    return consultas

@app.get("/api/consultas/{consulta_id}", tags=["Consultas"])
async def buscar_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    result = db.query(models.Consulta, models.Animal).join(
        models.Animal, models.Consulta.animal_id == models.Animal.id
    ).filter(models.Consulta.id == consulta_id).first()

    if not result:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    consulta, animal = result
    return {
        "id": consulta.id,
        "animal_id": consulta.animal_id,
        "animal_nome": animal.nome,
        "animal_especie": animal.especie,
        "animal_foto": animal.foto_url,
        "data_consulta": consulta.data_consulta.isoformat(),
        "veterinario": consulta.veterinario,
        "motivo": consulta.motivo,
        "diagnostico": consulta.diagnostico,
        "tratamento": consulta.tratamento,
        "medicamentos": consulta.medicamentos,
        "peso_consulta": float(consulta.peso_consulta) if consulta.peso_consulta else None,
        "retorno": str(consulta.retorno) if consulta.retorno else None,
        "status": consulta.status,
        "observacoes": consulta.observacoes,
        "created_at": consulta.created_at.isoformat(),
    }

@app.post("/api/consultas", status_code=201, tags=["Consultas"])
async def criar_consulta(
    consulta: ConsultaCreate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    animal = db.query(models.Animal).filter(models.Animal.id == consulta.animal_id).first()
    if not animal:
        raise HTTPException(status_code=404, detail="Animal não encontrado")

    nova_consulta = models.Consulta(**consulta.model_dump())
    db.add(nova_consulta)
    db.commit()
    db.refresh(nova_consulta)
    return {"id": nova_consulta.id, "message": "Consulta cadastrada com sucesso"}

@app.put("/api/consultas/{consulta_id}", tags=["Consultas"])
async def atualizar_consulta(
    consulta_id: int,
    consulta_data: ConsultaUpdate,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    consulta = db.query(models.Consulta).filter(models.Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")

    update_data = consulta_data.model_dump(exclude_unset=True)
    for field, value in update_data.items():
        setattr(consulta, field, value)

    db.commit()
    db.refresh(consulta)
    return {"message": "Consulta atualizada com sucesso"}

@app.delete("/api/consultas/{consulta_id}", tags=["Consultas"])
async def deletar_consulta(
    consulta_id: int,
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    consulta = db.query(models.Consulta).filter(models.Consulta.id == consulta_id).first()
    if not consulta:
        raise HTTPException(status_code=404, detail="Consulta não encontrada")
    db.delete(consulta)
    db.commit()
    return {"message": "Consulta removida com sucesso"}

@app.get("/api/dashboard", tags=["Dashboard"])
async def dashboard_stats(
    db: Session = Depends(get_db),
    current_user: str = Depends(get_current_user)
):
    total_animais = db.query(models.Animal).count()
    total_consultas = db.query(models.Consulta).count()
    consultas_agendadas = db.query(models.Consulta).filter(models.Consulta.status == "agendada").count()
    consultas_realizadas = db.query(models.Consulta).filter(models.Consulta.status == "realizada").count()

    hoje = datetime.now().date()
    consultas_hoje = db.query(models.Consulta).filter(
        models.Consulta.data_consulta >= datetime.combine(hoje, datetime.min.time()),
        models.Consulta.data_consulta < datetime.combine(hoje + timedelta(days=1), datetime.min.time())
    ).count()

    return {
        "total_animais": total_animais,
        "total_consultas": total_consultas,
        "consultas_agendadas": consultas_agendadas,
        "consultas_realizadas": consultas_realizadas,
        "consultas_hoje": consultas_hoje,
    }

@app.get("/", tags=["Health"])
async def root():
    return {"status": "online", "message": "Clínica Veterinária API v1.0"}
