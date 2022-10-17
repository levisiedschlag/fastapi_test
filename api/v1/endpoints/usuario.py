from typing import List, Optional, Any
from fastapi import APIRouter, status, Depends, HTTPException, Response
from fastapi.security import OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from models.usuario_model import UsuarioModel
from schemas.usuario_schema import UsuarioSchemaArtigos,UsuarioSchemaBase, UsuarioSchemaCreate, UsuarioSchemaUp
from core.deps import get_session, get_current_user
from core.security import gerar_hash_senha
from core.auth import autenticar, criar_token_acesso

router = APIRouter()

# GET LOGADO
@router.get('/logado', response_model=UsuarioSchemaBase)
def get_logado(usuario_logado:UsuarioModel=Depends(get_current_user)):
    return usuario_logado

# POST / SIGN-UP
@router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=UsuarioSchemaBase)
async def post_usuario(usuario:UsuarioSchemaCreate, db:AsyncSession=Depends(get_session)):
    novo_usuario:UsuarioModel=UsuarioModel(
        nome=usuario.nome, 
        sobrenome=usuario.sobrenome,
        email=usuario.email,
        senha=gerar_hash_senha(usuario.senha),
        eh_admin=usuario.eh_admin
        )