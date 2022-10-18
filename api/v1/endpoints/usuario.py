from typing import List, Optional, Any
from unittest import result
from urllib.error import ContentTooShortError
from fastapi import APIRouter, Query, status, Depends, HTTPException, Response
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

# POST / SIGN-UP / CRIAR
@router.post('/signup', status_code=status.HTTP_201_CREATED, response_model=UsuarioSchemaBase)
async def post_usuario(usuario: UsuarioSchemaCreate, db: AsyncSession = Depends(get_session)):
    novo_usuario: UsuarioModel = UsuarioModel(
        nome=usuario.nome, 
        sobrenome=usuario.sobrenome,
        email=usuario.email, 
        senha=gerar_hash_senha(usuario.senha), 
        eh_admin=usuario.eh_admin
        )
    async with db as session:
        try:
            session.add(novo_usuario)
            await session.commit()
            return novo_usuario
        except:
            raise HTTPException(status_code=status.HTTP_406_NOT_ACCEPTABLE,
                                detail='Já existe um usuário com este email cadastrado.')

# BUSCAR USUARIOS
@router.get('/', status_code=status.HTTP_200_OK, response_model=List[UsuarioSchemaBase])
async def get_usuarios(db:AsyncSession=Depends(get_session)):
    async with db as session:
        query=select(UsuarioModel)
        result=await session.execute(query)
        usuarios:List[UsuarioSchemaBase]=result.scalars().unique().all()
        return usuarios

# BUSCAR USUARIO
@router.get('/{usuario_id}', status_code=status.HTTP_200_OK, response_model=UsuarioSchemaArtigos)
async def get_usuario(usuario_id:int, db:AsyncSession=Depends(get_session)):
    async with db as session:
        query=select(UsuarioModel).filter(UsuarioModel.id==usuario_id)
        result=await session.execute(query)
        usuario:UsuarioSchemaArtigos=result.scalars().unique().one_or_none()
        if usuario:
            return usuario
        else:
            raise HTTPException(detail="Usuário não encontrado", status_code=status.HTTP_404_NOT_FOUND)

# EDITAR USUARIO
@router.put('/{usuario_id}', status_code=status.HTTP_202_ACCEPTED, response_model=UsuarioSchemaBase)
async def put_usuario(usuario_id:int,usuario:UsuarioSchemaUp , db:AsyncSession=Depends(get_session)):
    async with db as session:
        query=select(UsuarioModel).filter(UsuarioModel.id==usuario_id)
        result=await session.execute(query)
        usuario_up:UsuarioSchemaBase=result.scalars().unique().one_or_none()
        if usuario_up:
            if usuario.nome:
                usuario_up.nome=usuario.nome
            if usuario.sobrenome:
                usuario_up.sobrenome=usuario.sobrenome
            if usuario.email:
                usuario_up.email=usuario.email
            if usuario.eh_admin:
                usuario_up.eh_admin=usuario.eh_admin
            if usuario.senha:
                usuario_up.senha=gerar_hash_senha(usuario.senha)
            await session.commit()
            return usuario_up
        else:
            raise HTTPException(detail="Usuário não encontrado", status_code=status.HTTP_404_NOT_FOUND)

# DELETE USUARIO
@router.delete('/{usuario_id}', status_code=status.HTTP_204_NO_CONTENT)
async def delete_usuario(usuario_id:int, db:AsyncSession=Depends(get_session)):
    async with db as session:
        query=select(UsuarioModel).filter(UsuarioModel.id==usuario_id)
        result=await session.execute(query)
        usuario_del:UsuarioModel=result.scalars().unique().one_or_none()
        if usuario_del:
            await session.delete(usuario_del)
            await session.commit()
            return Response(status_code=status.HTTP_204_NO_CONTENT)
        else:
            raise HTTPException(detail="Usuário não encontrado", status_code=status.HTTP_404_NOT_FOUND)

# LOGIN
@router.post('/login')
async def login(form_data:OAuth2PasswordRequestForm=Depends(), db:AsyncSession=Depends(get_session)):
    usuario=await autenticar(email=form_data.username, senha=form_data.password, db=db)
    if not usuario:
        raise HTTPException(detail="Dados incorretos", status_code=status.HTTP_401_UNAUTHORIZED)
    else:
        return JSONResponse(content={"access_token":criar_token_acesso(sub=usuario.id)}, status_code=status.HTTP_200_OK)