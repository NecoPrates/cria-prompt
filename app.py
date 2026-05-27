from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///blog.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# ============ MODELOS ============
class Categoria(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(100), nullable=False, unique=True)
    artigos = db.relationship('Artigo', backref='categoria', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Categoria {self.nome}>'


class Artigo(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    titulo = db.Column(db.String(200), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    categoria_id = db.Column(db.Integer, db.ForeignKey('categoria.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)
    data_atualizacao = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    comentarios = db.relationship('Comentario', backref='artigo', lazy=True, cascade='all, delete-orphan')

    def __repr__(self):
        return f'<Artigo {self.titulo}>'


class Comentario(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    autor = db.Column(db.String(100), nullable=False)
    conteudo = db.Column(db.Text, nullable=False)
    artigo_id = db.Column(db.Integer, db.ForeignKey('artigo.id'), nullable=False)
    data_criacao = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Comentario de {self.autor}>'


# ============ ROTAS ============
@app.route('/')
def index():
    artigos = Artigo.query.order_by(Artigo.data_criacao.desc()).all()
    categorias = Categoria.query.all()
    return render_template('index.html', artigos=artigos, categorias=categorias)


@app.route('/artigo/<int:id>')
def ver_artigo(id):
    artigo = Artigo.query.get_or_404(id)
    return render_template('artigo.html', artigo=artigo)


@app.route('/admin')
def admin():
    artigos = Artigo.query.all()
    categorias = Categoria.query.all()
    return render_template('admin.html', artigos=artigos, categorias=categorias)


@app.route('/admin/novo-artigo', methods=['GET', 'POST'])
def novo_artigo():
    if request.method == 'POST':
        titulo = request.form.get('titulo')
        conteudo = request.form.get('conteudo')
        categoria_id = request.form.get('categoria_id')

        artigo = Artigo(titulo=titulo, conteudo=conteudo, categoria_id=categoria_id)
        db.session.add(artigo)
        db.session.commit()
        return redirect(url_for('admin'))

    categorias = Categoria.query.all()
    return render_template('novo_artigo.html', categorias=categorias)


@app.route('/admin/editar-artigo/<int:id>', methods=['GET', 'POST'])
def editar_artigo(id):
    artigo = Artigo.query.get_or_404(id)
    if request.method == 'POST':
        artigo.titulo = request.form.get('titulo')
        artigo.conteudo = request.form.get('conteudo')
        artigo.categoria_id = request.form.get('categoria_id')
        artigo.data_atualizacao = datetime.utcnow()
        db.session.commit()
        return redirect(url_for('admin'))

    categorias = Categoria.query.all()
    return render_template('editar_artigo.html', artigo=artigo, categorias=categorias)


@app.route('/admin/deletar-artigo/<int:id>')
def deletar_artigo(id):
    artigo = Artigo.query.get_or_404(id)
    db.session.delete(artigo)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/admin/categoria/novo', methods=['POST'])
def nova_categoria():
    nome = request.form.get('nome')
    categoria = Categoria(nome=nome)
    db.session.add(categoria)
    db.session.commit()
    return redirect(url_for('admin'))


@app.route('/comentario/novo', methods=['POST'])
def novo_comentario():
    artigo_id = request.form.get('artigo_id')
    autor = request.form.get('autor')
    conteudo = request.form.get('conteudo')

    comentario = Comentario(autor=autor, conteudo=conteudo, artigo_id=artigo_id)
    db.session.add(comentario)
    db.session.commit()
    return redirect(url_for('ver_artigo', id=artigo_id))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
