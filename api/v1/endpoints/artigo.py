from typing import List
from fastapi import APIRouter, status, Depends, HTTPException, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.artigo_model import ArtigoModel
from models.usuario_model import UsuarioModel
from schemas.artigo_schema import ArtigoSchema
from core.deps import get_session, get_current_user

router = APIRouter()

# POST
@router.post('/', status_code=status.HTTP_201_CREATED, response_model=ArtigoSchema)

async def post_artigo(artigo:ArtigoSchema, usuario_logado:UsuarioModel=Depends(get_current_user), db:AsyncSession=Depends(get_session)):
    
    pass