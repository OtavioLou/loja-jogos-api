from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database import SessionLocal
from models import Jogo, Plataforma, Categoria
from schemas import (
    JogoCreateSchema,
    JogoUpdateSchema,
    JogoResponseSchema
)


router = APIRouter(
    prefix="/jogos",
    tags=["Jogos"]
)


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()



@router.post(
    "/",
    response_model=JogoResponseSchema,
    status_code=status.HTTP_201_CREATED
)
def criar_jogo(
    jogo: JogoCreateSchema,
    db: Session = Depends(get_db)
):

   
    plataforma = db.query(Plataforma).filter(
        Plataforma.id == jogo.plataforma_id
    ).first()

    if not plataforma:
        raise HTTPException(
            status_code=404,
            detail="Plataforma não cadastrada."
        )

    
    categoria = db.query(Categoria).filter(
        Categoria.id == jogo.categoria_id
    ).first()

    if not categoria:
        raise HTTPException(
            status_code=404,
            detail="Categoria não cadastrada."
        )

    duplicado = db.query(Jogo).filter(
        Jogo.nome.ilike(jogo.nome),
        Jogo.plataforma_id == jogo.plataforma_id
    ).first()

    if duplicado:
        raise HTTPException(
            status_code=409,
            detail="Já existe um jogo com esse nome nessa plataforma."
        )

    novo_jogo = Jogo(
        nome=jogo.nome,
        preco=jogo.preco,
        plataforma_id=jogo.plataforma_id,
        categoria_id=jogo.categoria_id,
        usuario=jogo.usuario
    )

    db.add(novo_jogo)
    db.commit()
    db.refresh(novo_jogo)

    return novo_jogo



@router.get("/", response_model=list[JogoResponseSchema])
def listar_jogos(
    nome: str | None = None,
    plataforma_id: int | None = None,
    categoria_id: int | None = None,
    preco_max: float | None = None,
    db: Session = Depends(get_db)
):

    consulta = db.query(Jogo)

    if nome:
        consulta = consulta.filter(Jogo.nome.ilike(f"%{nome}%"))

    if plataforma_id is not None:
        consulta = consulta.filter(Jogo.plataforma_id == plataforma_id)

    if categoria_id is not None:
        consulta = consulta.filter(Jogo.categoria_id == categoria_id)

    if preco_max is not None:
        consulta = consulta.filter(Jogo.preco <= preco_max)

    return consulta.all()



@router.get("/{jogo_id}", response_model=JogoResponseSchema)
def buscar_jogo(
    jogo_id: int,
    db: Session = Depends(get_db)
):

    jogo = db.query(Jogo).filter(
        Jogo.id == jogo_id
    ).first()

    if not jogo:
        raise HTTPException(
            status_code=404,
            detail="Jogo não encontrado."
        )

    return jogo



@router.put("/{jogo_id}", response_model=JogoResponseSchema)
def atualizar_jogo(
    jogo_id: int,
    jogo_atualizado: JogoUpdateSchema,
    db: Session = Depends(get_db)
):

    
    jogo = db.query(Jogo).filter(
        Jogo.id == jogo_id
    ).first()

    if not jogo:
        raise HTTPException(
            status_code=404,
            detail="Jogo não encontrado."
        )

    plataforma = db.query(Plataforma).filter(
        Plataforma.id == jogo_atualizado.plataforma_id
    ).first()

    if not plataforma:
        raise HTTPException(
            status_code=404,
            detail="Plataforma não cadastrada."
        )

    categoria = db.query(Categoria).filter(
        Categoria.id == jogo_atualizado.categoria_id
    ).first()

    if not categoria:
        raise HTTPException(
            status_code=404,
            detail="Categoria não cadastrada."
        )

    duplicado = db.query(Jogo).filter(
        Jogo.nome.ilike(jogo_atualizado.nome),
        Jogo.plataforma_id == jogo_atualizado.plataforma_id,
        Jogo.id != jogo_id
    ).first()

    if duplicado:
        raise HTTPException(
            status_code=409,
            detail="Já existe um jogo com esse nome nessa plataforma."
        )

    jogo.nome = jogo_atualizado.nome
    jogo.preco = jogo_atualizado.preco
    jogo.plataforma_id = jogo_atualizado.plataforma_id
    jogo.categoria_id = jogo_atualizado.categoria_id

    db.commit()
    db.refresh(jogo)

    return jogo


@router.delete("/{jogo_id}")
def deletar_jogo(
    jogo_id: int,
    db: Session = Depends(get_db)
):

    jogo = db.query(Jogo).filter(
        Jogo.id == jogo_id
    ).first()

    if not jogo:
        raise HTTPException(
            status_code=404,
            detail="Jogo não encontrado."
        )

    db.delete(jogo)
    db.commit()

    return {
        "mensagem": "Jogo excluído com sucesso."
    }