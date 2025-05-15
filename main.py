from flask import Flask, render_template, request, redirect, flash
from datetime import datetime, timedelta

app = Flask(__name__)
app.secret_key = 'biblioteca_virtual'

livros = []

@app.route('/')
def index():
    return render_template('index.html', livros=livros)

@app.route('/catalogo')
def catalogo():
    return render_template('catalogo.html', livros=livros)

@app.route('/emprestimos')
def emprestimos():
    livros_emprestados = [l for l in livros if l['emprestado']]
    return render_template('emprestimos.html', livros=livros_emprestados)

@app.route('/adicionar', methods=['GET', 'POST'])
def adicionar():
    if request.method == 'POST':
        try:
            titulo = request.form['titulo']
            autor = request.form['autor']
            ano = int(request.form['ano'])
            if ano < 0 or ano > 2025:
                raise ValueError('Ano inválido. Informe um ano entre 0 e 2025.')
            codigo = len(livros)
            novo_livro = {
                'codigo': codigo,
                'titulo': titulo,
                'autor': autor,
                'ano': ano,
                'emprestado': False,
                'data_emprestimo': None,
                'data_devolucao': None
            }
            livros.append(novo_livro)
            flash(f"Livro {titulo} adicionado com sucesso!")
            return redirect('/')
        except Exception as e:
            return render_template('erro.html', mensagem=f'Erro ao adicionar livro: {e}')
    return render_template('form.html', titulo='Adicionar Livro', livro=None)

@app.route('/editar/<int:codigo>', methods=['GET', 'POST'])
def editar(codigo):
    try:
        livro = livros[codigo]
        if request.method == 'POST':
            livro['titulo'] = request.form['titulo']
            livro['autor'] = request.form['autor']
            ano = int(request.form['ano'])
            if ano < 0 or ano > 2025:
                raise ValueError('Ano inválido. Informe um ano entre 0 e 2025.')
            livro['ano'] = ano
            flash(f"Livro {livro['titulo']} editado com sucesso!")
            return redirect('/')
        return render_template('form.html', titulo='Editar Livro', livro=livro)
    except Exception as e:
        return render_template('erro.html', mensagem=f'Erro ao editar livro: {e}')

@app.route('/excluir/<int:codigo>')
def excluir(codigo):
    try:
        titulo = livros[codigo]['titulo']
        livros.pop(codigo)
        for ADE in range(len(livros)):
            livros[ADE]['codigo'] = ADE

        #for ADE, livro in enumerate(livros): # enumerate serve para substituir o ADE=0 ---- ADE+=1
         #   livro['codigo'] = ADE

        flash(f"Livro {titulo} excluído com sucesso!")
    except Exception as e:
        return render_template('erro.html', mensagem=f'Erro ao excluir livro: {e}')
    return redirect('/')

@app.route('/emprestar/<int:codigo>')
def emprestar(codigo):
    try:
        livro = livros[codigo]
        agora = datetime.now()
        livro['emprestado'] = True
        livro['data_emprestimo'] = agora
        livro['data_devolucao'] = agora + timedelta(days=7)
        data_str = livro['data_devolucao'].strftime('%d/%m/%Y')
        flash(f"Livro {livro['titulo']} emprestado até {data_str}.")
    except Exception as e:
        return render_template('erro.html', mensagem=f'Erro ao emprestar livro: {e}')
    return redirect('/')

@app.route('/devolver/<int:codigo>')
def devolver(codigo):
    try:
        livro = livros[codigo]
        hoje = datetime.now()
        atraso = (hoje - livro['data_devolucao']).days
        if hoje < livro['data_emprestimo']:
            return render_template('erro.html', mensagem='Erro, não aceitamos devolução de um viajante do tempo!')
        if atraso > 0:
            multa = 10 + (10 * 0.01 * atraso)
            flash(f"Livro devolvido com {atraso} dias de atraso. Multa: R$ {multa:.2f}")
        else:
            flash(f"Livro {livro['titulo']} devolvido sem atraso.")
        livro['emprestado'] = False
        livro['data_emprestimo'] = None
        livro['data_devolucao'] = None
    except Exception as e:
        return render_template('erro.html', mensagem=f'Erro ao devolver livro: {e}')
    return redirect('/')

if __name__ == '__main__':
    app.run(debug=True)
