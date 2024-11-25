from flask import request, jsonify
from werkzeug.security import check_password_hash, generate_password_hash
from app import app, db
from models import Funcionario, Problema, Materiais, ProblemaMaterial, Cargo, Prioridade, Status
from datetime import datetime
import os
import uuid


upload_folder = 'static/uploads'
os.makedirs(upload_folder, exist_ok=True)
@app.route('/funcionario', methods=['POST'])
def cadastrar_funcionario():
    data = request.get_json()
    nome = data.get('nome')
    nif = data.get('nif')
    senha = data.get('senha')
    cargo = data.get('cargo')

    if Funcionario.query.filter_by(nif=nif).first():
        return jsonify(mensagem="Funcionário com este NIF já está cadastrado!"), 400

    try:
        cargo_enum = Cargo[cargo]
        novo_funcionario = Funcionario(
            nome=nome,
            nif=nif,
            senha=generate_password_hash(senha),
            cargo=cargo_enum
        )
        db.session.add(novo_funcionario)
        db.session.commit()
        return jsonify(mensagem="Funcionário cadastrado com sucesso!"), 201
    except KeyError:
        cargos_validos = [cargo.name for cargo in Cargo]
        return jsonify(mensagem=f"Cargo inválido! Cargos válidos são: {', '.join(cargos_validos)}"), 400
    except Exception as e:
        db.session.rollback()
        return jsonify(mensagem=f"Erro ao salvar: {str(e)}"), 500

@app.route('/funcionario', methods=['GET'])
def listar_funcionarios():
    nif = request.args.get('nif')
    if nif:
        funcionario = Funcionario.query.filter_by(nif=nif).first()
        if funcionario:
            return jsonify({
                'id_funcionario': funcionario.id_funcionario,
                'nome': funcionario.nome,
                'nif': funcionario.nif,
                'cargo': funcionario.cargo.name
            }), 200
        else:
            return jsonify(mensagem="Funcionário não encontrado!"), 404
    else:
        funcionarios = Funcionario.query.all()
        return jsonify(funcionarios=[{
            'id_funcionario': f.id_funcionario,
            'nome': f.nome,
            'nif': f.nif,
            'cargo': f.cargo.name
        } for f in funcionarios]), 200

@app.route('/funcionario/<int:id_funcionario>', methods=['PUT'])
def atualizar_funcionario(id_funcionario):
    data = request.get_json()
    funcionario = Funcionario.query.get(id_funcionario)

    if not funcionario:
        return jsonify(mensagem="Funcionário não encontrado!"), 404

    try:
        nome = data.get('nome', funcionario.nome)
        nif = data.get('nif', funcionario.nif)
        cargo = data.get('cargo', funcionario.cargo.name)

        if Funcionario.query.filter_by(nif=nif).first() and nif != funcionario.nif:
            return jsonify(mensagem="Já existe um funcionário com este NIF!"), 400

        cargo_enum = Cargo[cargo]

        funcionario.nome = nome
        funcionario.nif = nif
        funcionario.senha = generate_password_hash(data.get('senha', funcionario.senha))
        funcionario.cargo = cargo_enum

        db.session.commit()
        return jsonify(mensagem="Funcionário atualizado com sucesso!"), 200
    except KeyError:
        cargos_validos = [cargo.name for cargo in Cargo]
        return jsonify(mensagem=f"Cargo inválido! Cargos válidos são: {', '.join(cargos_validos)}"), 400
    except Exception as e:
        db.session.rollback()
        return jsonify(mensagem=f"Erro ao atualizar: {str(e)}"), 500

@app.route('/funcionario/<int:id_funcionario>', methods=['DELETE'])
def deletar_funcionario(id_funcionario):
    funcionario = Funcionario.query.get(id_funcionario)

    if not funcionario:
        return jsonify(mensagem="Funcionário não encontrado!"), 404

    try:
        db.session.delete(funcionario)
        db.session.commit()
        return jsonify(mensagem="Funcionário deletado com sucesso!"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(mensagem=f"Erro ao deletar: {str(e)}"), 500

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    nif = data.get('nif')
    senha = data.get('senha')

    user = Funcionario.query.filter_by(nif=nif).first()

    if user and check_password_hash(user.senha, senha):
        response_message = "Login bem-sucedido!"
        cargo_str = str(user.cargo)
        if user.cargo == Cargo.funcionario_geral:
            return jsonify(mensagem=f"{response_message} Redirecionando para a página de visualização.", id_funcionario=user.id_funcionario, cargo=cargo_str), 200
        elif user.cargo == Cargo.funcionario_manutencao:
            return jsonify(mensagem=f"{response_message} Redirecionando para a página de problemas designados.", id_funcionario=user.id_funcionario, cargo=cargo_str), 200
        elif user.cargo == Cargo.chefe_manutencao:
            return jsonify(mensagem=f"{response_message} Redirecionando para a tela de designação.", id_funcionario=user.id_funcionario, cargo=cargo_str), 200
        else:
            return jsonify(mensagem="Cargo inválido!"), 400
    else:
        return jsonify(mensagem="NIF ou senha incorretos!"), 400
@app.route('/materiais', methods=['POST'])
def cadastrar_material():
    data = request.get_json()
    nome = data.get('nome')
    unidade = data.get('unidade')
    quantidade_estoque = data.get('quantidade_estoque')
    valor = data.get('valor')

    if Materiais.query.filter_by(nome=nome).first():
        return jsonify(mensagem="Material com este nome já está cadastrado!"), 400

    try:
        novo_material = Materiais(
            nome=nome,
            unidade=unidade,
            quantidade_estoque=quantidade_estoque,
            valor=valor
        )
        db.session.add(novo_material)
        db.session.commit()
        return jsonify(mensagem="Material cadastrado com sucesso!"), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(mensagem=f"Erro ao salvar: {str(e)}"), 500

@app.route('/materiais', methods=['GET'])
def listar_materiais():
    materiais = Materiais.query.all()
    return jsonify(materiais=[{
        'id_material': m.id_material,
        'nome': m.nome,
        'unidade': m.unidade,
        'quantidade_estoque': str(m.quantidade_estoque),
        'valor': str(m.valor)
    } for m in materiais]), 200

@app.route('/materiais/<int:id_material>', methods=['PUT'])
def atualizar_material(id_material):
    data = request.get_json()
    material = Materiais.query.get(id_material)

    if not material:
        return jsonify(mensagem="Material não encontrado!"), 404

    try:
        material.nome = data.get('nome', material.nome)
        material.unidade = data.get('unidade', material.unidade)
        material.quantidade_estoque = data.get('quantidade_estoque', material.quantidade_estoque)
        material.valor = data.get('valor', material.valor)

        db.session.commit()
        return jsonify(mensagem="Material atualizado com sucesso!"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(mensagem=f"Erro ao atualizar: {str(e)}"), 500

@app.route('/materiais/<int:id_material>', methods=['DELETE'])
def deletar_material(id_material):
    material = Materiais.query.get(id_material)

    if not material:
        return jsonify(mensagem="Material não encontrado!"), 404

    try:
        db.session.delete(material)
        db.session.commit()
        return jsonify(mensagem="Material deletado com sucesso!"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(mensagem=f"Erro ao deletar: {str(e)}"), 500


@app.route('/problema', methods=['POST'])
def cadastrar_problema():
    # Imprime para depuração
    print("Recebendo dados para cadastrar problema...")

    data = request.get_json()
    print("Dados recebidos:", data)

    descricao = data.get('descricao')
    local = data.get('local')
    prontuario = data.get('prontuario')
    prioridade = data.get('prioridade')
    status = data.get('status')
    id_funcionario = data.get('id_funcionario')
    obs_funcionario = data.get('obs_funcionario')
    datetime_inicio = data.get('datetime_inicio')
    datetime_finalizado = data.get('datetime_finalizado')
    quanto_gastou = data.get('quanto_gastou')

    novo_problema = Problema(
        descricao=descricao,
        local=local,
        prontuario=prontuario,
        prioridade=Prioridade[prioridade] if prioridade else 0,
        status=Status[status] if status else Status.Aberto,
        obs_funcionario=obs_funcionario,
        datetime_inicio=datetime_inicio,
        datetime_finalizado=datetime_finalizado,
        quanto_gastou=quanto_gastou,
        id_funcionario=id_funcionario
    )

    try:
        # Adiciona o novo problema ao banco de dados
        db.session.add(novo_problema)
        db.session.commit()

        # Retorna a resposta de sucesso
        return jsonify(mensagem="Problema cadastrado com sucesso!", problema=novo_problema.id_problema), 201

    except KeyError as e:
        return jsonify(mensagem=f"Erro: '{str(e)}' é inválido."), 400
    except Exception as e:
        # Se houver qualquer outro erro, faz rollback e retorna erro
        db.session.rollback()
        return jsonify(mensagem=f"Erro ao salvar: {str(e)}"), 500


@app.route('/problema/<int:id_problema>', methods=['PUT'])
def atualizar_problema(id_problema):
    data = request.get_json()
    problema = Problema.query.get(id_problema)

    if not problema:
        return jsonify(mensagem="Problema não encontrado!"), 404

    try:
        problema.descricao = data.get('titulo', problema.descricao)
        problema.local = data.get('local', problema.local)
        problema.status = Status[data.get('status', problema.status.name)]
        problema.obs_funcionario = data.get('observacao', problema.obs_funcionario)
        problema.prioridade = data.get('prioridade', problema.prioridade)

        db.session.commit()
        return jsonify(mensagem="Problema atualizado com sucesso!"), 200
    except KeyError as e:
        return jsonify(mensagem=f"Valor inválido para prioridade ou status: {str(e)}"), 400
    except Exception as e:
        db.session.rollback()
        return jsonify(mensagem=f"Erro ao atualizar: {str(e)}"), 500

@app.route('/problema/<int:id_problema>/designar', methods=['PUT'])
def designar_funcionario(id_problema):
    problema = Problema.query.get(id_problema)


    if not problema:
        return jsonify(mensagem="Problema não encontrado!"), 404

    data = request.get_json()
    id_funcionario = data.get('id_funcionario')

    if not id_funcionario:
        return jsonify(mensagem="ID do funcionário não fornecido!"), 400
    funcionario = Funcionario.query.get(id_funcionario)
    if not funcionario:
        return jsonify(mensagem="Funcionário não encontrado!"), 404
    try:
        problema.id_funcionario = id_funcionario
        db.session.commit()
        return jsonify(mensagem="Funcionário designado ao problema com sucesso!"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(mensagem=f"Erro ao designar funcionário: {str(e)}"), 500
@app.route('/problema/<int:id_problema>', methods=['DELETE'])
def deletar_problema(id_problema):
    problema = Problema.query.get(id_problema)
    if not problema:
        return jsonify(mensagem="Problema não encontrado!"), 404
    try:
        if problema.caminho_imagem:
            image_path = os.path.join(upload_folder, problema.caminho_imagem)
            if os.path.exists(image_path):
                os.remove(image_path)

        db.session.delete(problema)
        db.session.commit()
        return jsonify(mensagem="Problema deletado com sucesso!"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(mensagem=f"Erro ao deletar: {str(e)}"), 500


@app.route('/problemas', methods=['GET'])
def listar_problemas():
    # Obtém o id_funcionario da query string (caso exista)
    id_funcionario = request.args.get('id_funcionario')

    if id_funcionario:
        # Filtra os problemas com base no id_funcionario
        # SELECT * FROM problema WHERE id_funcionario = id_funcionario ORDER BY prioridade DESC
        problemas = Problema.query.filter_by(id_funcionario=id_funcionario).order_by(Problema.prioridade.desc()).all()

    else:
        # Retorna todos os problemas se id_funcionario não for fornecido
        problemas = Problema.query.order_by(Problema.prioridade.desc()).all()

        print(problemas)

    resultado = [
        {
            'id_problema': p.id_problema,
            'descricao': p.descricao,
            'local': p.local,
            'prontuario': p.prontuario,
            'prioridade': p.prioridade,
            'status': p.status.value,
            'obs_funcionario': p.obs_funcionario,
            'datetime_inicio': p.datetime_inicio,
            'datetime_finalizado': p.datetime_finalizado,
            'quanto_gastou': float(p.quanto_gastou) if p.quanto_gastou else None,
            'id_funcionario': p.id_funcionario,
        } for p in problemas
    ]

    return jsonify(problemas=resultado), 200

@app.route('/problema_material', methods=['POST'])
def cadastrar_problema_material():
    data = request.get_json()
    id_funcionario = data.get('id_funcionario')
    id_problema = data.get('id_problema')
    id_material = data.get('id_material')
    quantidade = data.get('quantidade')
    valor_total = data.get('valor_total')

    funcionario = Funcionario.query.get(id_funcionario)
    problema = Problema.query.get(id_problema)
    material = Materiais.query.get(id_material)

    if not funcionario or not problema or not material:
        return jsonify(mensagem="Funcionário, problema ou material não encontrado!"), 404

    try:
        problema_material = ProblemaMaterial(
            id_funcionario=id_funcionario,
            id_problema=id_problema,
            id_material=id_material,
            quantidade=quantidade,
            valor_total=valor_total
        )
        db.session.add(problema_material)
        db.session.commit()
        return jsonify(mensagem="Associação de problema e material cadastrada com sucesso!"), 201
    except Exception as e:
        db.session.rollback()
        return jsonify(mensagem=f"Erro ao salvar: {str(e)}"), 500

@app.route('/problema_material', methods=['GET'])
def listar_problema_materiais():
    problema_materiais = ProblemaMaterial.query.all()
    return jsonify(problema_materiais=[{
        'id_funcionario': pm.id_funcionario,
        'id_problema': pm.id_problema,
        'id_material': pm.id_material,
        'quantidade': pm.quantidade,
        'valor_total': pm.valor_total
    } for pm in problema_materiais]), 200

@app.route('/problema_material/<int:id>', methods=['GET'])
def detalhar_problema_material(id):
    problema_material = ProblemaMaterial.query.get(id)
    if problema_material:
        return jsonify({
            'id_funcionario': problema_material.id_funcionario,
            'id_problema': problema_material.id_problema,
            'id_material': problema_material.id_material,
            'quantidade': problema_material.quantidade,
            'valor_total': problema_material.valor_total
        }), 200
    else:
        return jsonify(mensagem="ProblemaMaterial não encontrado!"), 404

@app.route('/problema_material/<int:id>', methods=['PUT'])
def atualizar_problema_material(id):
    data = request.get_json()
    problema_material = ProblemaMaterial.query.get(id)

    if not problema_material:
        return jsonify(mensagem="ProblemaMaterial não encontrado!"), 404

    try:
        problema_material.id_funcionario = data.get('id_funcionario', problema_material.id_funcionario)
        problema_material.id_problema = data.get('id_problema', problema_material.id_problema)
        problema_material.id_material = data.get('id_material', problema_material.id_material)
        problema_material.quantidade = data.get('quantidade', problema_material.quantidade)
        problema_material.valor_total = data.get('valor_total', problema_material.valor_total)

        db.session.commit()
        return jsonify(mensagem="ProblemaMaterial atualizado com sucesso!"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(mensagem=f"Erro ao atualizar: {str(e)}"), 500

@app.route('/problema_material/<int:id>', methods=['DELETE'])
def deletar_problema_material(id):
    problema_material = ProblemaMaterial.query.get(id)

    if not problema_material:
        return jsonify(mensagem="ProblemaMaterial não encontrado!"), 404

    try:
        db.session.delete(problema_material)
        db.session.commit()
        return jsonify(mensagem="ProblemaMaterial deletado com sucesso!"), 200
    except Exception as e:
        db.session.rollback()
        return jsonify(mensagem=f"Erro ao deletar: {str(e)}"), 500
