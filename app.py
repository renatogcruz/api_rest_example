from itertools import count
from typing import Optional
from flask import Flask, request, jsonify
from flask_pydantic_spec import FlaskPydanticSpec, Response, Request
from pydantic import BaseModel, Field
from tinydb import TinyDB, Query
from tinydb.storages import MemoryStorage


server = Flask(__name__)
spec = FlaskPydanticSpec('flask', title='API REST Example')
spec.register(server)
database = TinyDB(storage=MemoryStorage)
c = count()


class QueryPessoa(BaseModel):
    id: Optional[int]
    nome: Optional[str]
    idade: Optional[int]


class Pessoa(BaseModel):
    id: Optional[int] = Field(default_factory=lambda: next(c))
    nome: str
    idade: int


class Pessoas(BaseModel):
    pessoas: Pessoa
    count: int


@server.get('/pessoas/<int:id>')  # rota, endpoint, recurso
@spec.validate(resp=Response(HTTP_200=Pessoa))
def buscar_pessoa(id):
    """Retorna uma Pessoa da base de dados."""
    try:
        pessoa = database.search(Query().id == id)[0]
    except IndexError:
        return {'message': 'Pessoa not found'}, 404

    return jsonify(pessoa)


@server.post('/pessoas')
@spec.validate(
    body=Request(Pessoa), resp=Response(HTTP_201=Pessoa)
)
def inserir_pessoa():
    """Insere uma Pessoa no banco de dados."""
    body = request.context.body.dict()
    database.insert(body)
    return body


@server.put('/pessoas/<int:id>')
@spec.validate(body=Request(Pessoa), resp=Response(HTTP_200=Pessoa))
def altera_pessoa(id):
    '''Altera uma Pessoa do banco de dados.'''
    Pessoa = Query()
    body = request.context.body.dict()
    database.update(body, Pessoa.id == id)
    return jsonify(body)


@server.delete('/pessoas/<int:id>')
@spec.validate(resp=Response(HTTP_200=Pessoa))
def deleta_pessoa(id):
    '''Remove uma Pessoa do banco de dados.'''
    Pessoa = Query()
    database.remove(Pessoa.id == id)
    return jsonify({})


server.run()
