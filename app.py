from flask import Flask, Response, request
from flask_sqlalchemy import SQLAlchemy
import mysql.connector
import json
import os
from dotenv import load_dotenv

load_dotenv(override=True)
app = Flask(__name__)
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = True
app.config["SQLALCHEMY_DATABASE_URI"] = f'mysql+pymysql://{os.getenv("MYSQL_USER")}:{os.getenv("MYSQL_PASSWORD")}@localhost/{os.getenv("MYSQL_DATABASE")}'
db = SQLAlchemy(app)

class Usuario(db.Model):
    __tablename__ = 'usuario'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    nome = db.Column(db.String(50))
    email = db.Column(db.String(100))
    
    #gerar objeto
    def to_json(self):
        return {"id": self.id, "nome": self.nome, "email": self.email}

#selecionar tudo 
@app.route("/usuario", methods=["GET"])
def seleciona_usuarios():
    usuario_objetos = Usuario.query.all()
    #para cada usuario em usuario_obejto, chama o metodo to_json()
    usuario_json = [usuario.to_json() for usuario in usuario_objetos]
    return gerar_response(200, "usuario",usuario_json, "ok")

#selecionar apenas um
@app.route("/usuario/<id>", methods=["GET"])
def selecionar_id(id):
    usuario_obejto = Usuario.query.filter_by(id=id).first()
    usuario_json = usuario_obejto.to_json()
    return gerar_response(200, "usuario", usuario_json)

#criar usuario
@app.route("/usuario", methods=["POST"])
def criar_usuario():
    body = request.get_json()
    try:
        usuario = Usuario(nome=body["nome"], email=body["email"])
        db.session.add(usuario)
        db.session.commit()
        return gerar_response(201, "usuario", usuario.to_json(), "Criado com sucesso")
    except Exception as e:
        print(e)
        return gerar_response(400, "usuario",{}, "Error ao cadastrar")
    
@app.route("/usuario/<id>", methods=["PUT"])
def atualiza_usuario(id):
    usuario_objeto = Usuario.query.filter_by(id=id).first()
    body = request.get_json()
    
    try:
        if('nome' in body):
            usuario_objeto.nome = body["nome"]
        if('email' in body):
            usuario_objeto.email = body["email"]
            
        db.session.add(usuario_objeto)
        db.session.commit()
        return gerar_response(200, "usuario", usuario_objeto.to_json(), "Atualizado com sucesso")
    except Exception as e:
        print("Erro" ,e)
        return gerar_response(400, "usuario",{}, "Error ao atualizar")
    
@app.route("/usuario/<id>", methods=["DELETE"])
def deletar_usuario(id):
    usuario_objeto = Usuario.query.filter_by(id=id).first()
    
    try:
        db.session.delete(usuario_objeto)
        db.session.commit()
        return gerar_response(200, "usuario", usuario_objeto.to_json(), "Deletado com sucesso")
    except Exception as e:
        print("Erro" ,e)
        return gerar_response(400, "usuario",{}, "Error ao deletar")

def gerar_response(status, nome_do_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_do_conteudo] = conteudo
    
    if(mensagem):
        body["mensagem"]= mensagem
        
    return Response(json.dumps(body), status=status, mimetype="application/json")

if __name__ == "__main__":
    app.run(debug=True)