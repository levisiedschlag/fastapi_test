from typing import List
from unittest import result
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
    novo_artigo:ArtigoModel = ArtigoModel(
        titulo=artigo.titulo,
        descricao=artigo.descricao,
        url_fonte=artigo.url_font,
        usuario_id=usuario_logado.id
        )
    db.add(novo_artigo)
    await db.commit()
    return novo_artigo

# GET LISTA DE ARTIGOS
@router.get('/', response_model=List[ArtigoSchema], status_code=status.HTTP_200_OK)
async def get_artigos(db:AsyncSession=Depends(get_session)):
    async with db as session:
        query = select(ArtigoModel)
        result = await session.execute(query)
        artigos:List[ArtigoModel]=result.scalars().unique().all()
        return artigos

# GET ARTIGO
@router.get('/{artigo_id}', response_model=ArtigoSchema, status_code=status.HTTP_200_OK)
async def get_artigo(artigo_id:int ,db:AsyncSession=Depends(get_session)):
    async with db as session:
        query=select(ArtigoModel).filter(ArtigoModel.id == artigo_id)
        result = await session.execute(query)
        artigo:ArtigoModel=result.scalars().unique().one_or_none()
        if artigo:
            return artigo
        else:
            raise HTTPException(detail='Artigo não encontrado', status_code=status.HTTP_404_NOT_FOUND)

# PUT ARTIGO
@router.put('/{artigo_id}', response_model=ArtigoSchema, status_code=status.HTTP_202_ACCEPTED)
async def put_artigo(artigo_id:int, artigo:ArtigoSchema, db:AsyncSession=Depends(get_session), usuario_logado:UsuarioModel=Depends(get_current_user)):
    async with db as session:
        query=select(ArtigoModel).filter(ArtigoModel.id==artigo_id)
        result=await session.execute(query)
        artigo_up:ArtigoModel=result.scalars().unique().one_or_none()
        if artigo_up:
            if artigo_up.titulo:
                artigo_up.titulo=artigo.titulo
            if artigo_up.descricao:
                artigo_up.descricao=artigo.descricao
            if artigo_up.criador:
                artigo_up.criador=usuario_logado.id
            if artigo_up.url_fonte:
                artigo_up.url_fonte=artigo.url_fonte

            return artigo_up
        else:
            raise HTTPException(detail='Artigo nao encontrado', status_code=status.HTTP_404_NOT_FOUND)
