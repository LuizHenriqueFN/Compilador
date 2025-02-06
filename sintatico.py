from lexico import TOKEN, Lexico
from semantico import Semantico

class Sintatico:
    
    def __init__(self, lexico: Lexico, nomeAlvo):
        self.lexico = lexico
        self.semantico = Semantico(nomeAlvo)

    def traduz(self):
        self.tokenLido = self.lexico.getToken()
        try:
            self.prog()
            print('Traduzido com sucesso.')
        except Exception as e:
            print(e)

    def consome(self, tokenAtual):
        (token, lexema, linha, coluna) = self.tokenLido
        if tokenAtual == token:
            self.tokenLido = self.lexico.getToken()
        else:
            msgTokenLido = TOKEN.msg(token)
            msgTokenAtual = TOKEN.msg(tokenAtual)
            print(f'Erro na linha {linha}, coluna {coluna}:')
            if token == TOKEN.ERRO:
                msg = lexema
            else:
                msg = msgTokenLido
            print(f'Era esperado "{msgTokenAtual}" mas veio "{msg}"')
            raise Exception
    
    def testaLexico(self):
        self.tokenLido = self.lexico.getToken()
        (token, _, _, _) = self.tokenLido
        while token != TOKEN.EOF:
            self.lexico.imprimeToken(self.tokenLido)
            self.tokenLido = self.lexico.getToken()
            (token, _, _, _) = self.tokenLido

#-------- segue a gramatica -----------------------------------------

    # <prog> -> <funcao> <restoFuncoes>
    def prog(self):
        self.semantico.gera(0, '# Codigo gerado pelo compilador\n')
        self.semantico.gera(0, 'class Programa:\n')
        self.semantico.gera(1, 'def __init__(self):\n')
        self.semantico.gera(2, 'pass\n\n')
        self.funcao(1)
        self.restoFuncoes(1)

        self.semantico.gera(0, '\nif __name__ == "__main__":\n')
        self.semantico.gera(1, 'programa = Programa()\n')
        self.semantico.gera(1, 'programa.main()\n')

    # <restoFuncoes> -> <funcao> <restoFuncoes> | LAMBDA
    def restoFuncoes(self, indentacao):
        if self.tokenLido[0] == TOKEN.FUNCTION:
            self.funcao(indentacao)
            self.restoFuncoes(indentacao)
        else:
            pass

    # <funcao> -> function ident ( <params> ) <tipoResultado> <corpo>
    def funcao(self, indentacao):
        self.consome(TOKEN.FUNCTION)  # Consome 'function'
        nome_funcao = self.tokenLido[1]  # Captura o identificador (nome da função)
        self.consome(TOKEN.IDENT)  # Consome o identificador
        self.consome(TOKEN.ABRE_PARENTESES)  # Consome '('
        args = self.params()  # Chama a produção 'params' para processar os parâmetros
        self.consome(TOKEN.FECHA_PARENTESES)  # Consome ')'
        args.append(self.tipoResultado()) 
        
        if args != [] and len(args) != 1:
            parametros = ', '.join([arg[0] for arg in args[:-1]])
            self.semantico.gera(indentacao, f'def {nome_funcao}(self, {parametros}):\n') 
        else:
            self.semantico.gera(indentacao, f'def {nome_funcao}(self):\n') 
         # Obtém o tipo da função (após '->' ou vazio)
        self.semantico.declara(nome_funcao, (TOKEN.FUNCTION, args))  # Atualiza com o tipo da função
        self.semantico.entra_escopo()  # Entra no escopo local da função
        for (nome_funcao, tipo) in args:
            if nome_funcao != 'retorno':
                self.semantico.declara(nome_funcao, tipo)
        self.corpo(indentacao+1)  # Processa o corpo da função
        self.semantico.sai_escopo()  # Sai do escopo local

    # <tipoResultado> -> LAMBDA | -> <tipo>
    def tipoResultado(self):
        if self.tokenLido[0] == TOKEN.SETA:
            self.consome(TOKEN.SETA)  # Consome '->'
            return ("retorno", self.tipo())  # Retorna o tipo após '->'
        else:
            return ("retorno", None)


    # <params> -> <tipo> ident <restoParams> | LAMBDA
    def params(self):
        if self.tokenLido[0] in [TOKEN.STRING, TOKEN.INT, TOKEN.FLOAT]:
            tipo = self.tipo()
            nome = self.tokenLido[1]
            self.consome(TOKEN.IDENT)
            args = list()
            args.append((nome, tipo))
            self.restoParams(args)
            return args
        else:
            return list()


    # <restoParams> -> LAMBDA | , <tipo> ident <restoParams>
    def restoParams(self, args: list):
        if self.tokenLido[0] == TOKEN.VIRGULA:
            self.consome(TOKEN.VIRGULA)
            tipo = self.tipo()
            nome = self.tokenLido[1]
            self.consome(TOKEN.IDENT)
            args.append((nome, tipo))
            self.restoParams(args)
        else:
            pass

    # <corpo> -> begin <declaracoes> <calculo> end
    def corpo(self, indentacao):
        self.consome(TOKEN.BEGIN)
        self.declaracoes()
        self.calculo(indentacao)
        self.consome(TOKEN.END)
        self.semantico.gera(0, '\n')

    # <declaracoes> -> <declara> <declaracoes> | LAMBDA
    def declaracoes(self):
        if self.tokenLido[0] in [TOKEN.STRING, TOKEN.INT, TOKEN.FLOAT]:
            self.declara()
            self.declaracoes()
        else:
            pass

    # <declara> -> <tipo> <idents> ;
    def declara(self):
        tipo = self.tipo()  # Isso retorna o tipo da variável
        variaveis = self.idents(list())
        for var in variaveis:
            self.semantico.declara(var, tipo)
        self.consome(TOKEN.PONTO_VIRGULA)


    # <idents> -> ident <restoIdents>
    def idents(self, variaveis: list):
        nome = self.tokenLido[1]
        variaveis.append(nome)
        self.consome(TOKEN.IDENT)
        self.restoIdents(variaveis)
        return variaveis

    # <restoIdents> -> , ident <restoIdents> | LAMBDA
    def restoIdents(self, variaveis: list):
        if self.tokenLido[0] == TOKEN.VIRGULA:
            self.consome(TOKEN.VIRGULA)
            nome = self.tokenLido[1]
            variaveis.append(nome)
            self.consome(TOKEN.IDENT)
            self.restoIdents(variaveis)
        else:
            pass

    # <tipo> -> string <opcLista> | int <opcLista> | float <opcLista>
    def tipo(self):
        if self.tokenLido[0] == TOKEN.STRING:
            self.consome(TOKEN.STRING)
            return (TOKEN.STRING, self.opcLista())  # Retorna 'string' ou 'string[list]'
        elif self.tokenLido[0] == TOKEN.INT:
            self.consome(TOKEN.INT)
            return (TOKEN.INT, self.opcLista())  # Retorna 'int' ou 'int[list]'
        elif self.tokenLido[0] == TOKEN.FLOAT:
            self.consome(TOKEN.FLOAT)
            return (TOKEN.FLOAT, self.opcLista())  # Retorna 'float' ou 'float[list]'


    # <opcLista> -> [ list ] | LAMBDA
    def opcLista(self):
        if self.tokenLido[0] == TOKEN.ABRE_COLCHETES:
            self.consome(TOKEN.ABRE_COLCHETES)
            self.consome(TOKEN.LIST)
            self.consome(TOKEN.FECHA_COLCHETES)
            return True  # Retorna o tipo como lista
        return False  # Retorna o tipo base, se não for lista


    # <retorna> -> return <expOpc> ;
    def retorna(self, indentacao = 0):
        self.consome(TOKEN.RETURN)
        texto = self.expOpc()
        self.semantico.gera(indentacao, f'return {texto}\n')
        self.consome(TOKEN.PONTO_VIRGULA)

    # <expOpc> -> LAMBDA | <exp>
    def expOpc(self):
        exp = [TOKEN.NOT, TOKEN.SOMA, TOKEN.SUBTRACAO, TOKEN.INTVAL, TOKEN.FLOATVAL, TOKEN.STRVAL, TOKEN.IDENT, TOKEN.ABRE_PARENTESES]
        if self.tokenLido[0] in exp:
            (_, lexema) = self.exp()
            return lexema
        else:
            return ''

    # <while> -> while ( <exp> ) <com>
    def _while_(self):
        self.consome(TOKEN.WHILE)
        self.consome(TOKEN.ABRE_PARENTESES)
        colunaErro = self.tokenLido[3]
        operacao = list()
        self.exp(operacao)
        resultado = self.semantico.verifica_operacao(operacao)
        if resultado[0] != TOKEN.BOOLEAN:
            raise Exception(f"Expressão inválida: linha {self.tokenLido[2]}, coluna {colunaErro}.")

        self.consome(TOKEN.FECHA_PARENTESES)
        self.com()

    # <for> -> for ident in <range> do <com>
    def _for_(self, indentacao = ''):
        self.consome(TOKEN.FOR)
        nome = self.tokenLido[1]
        self.consome(TOKEN.IDENT)
        tipo = self.semantico.obter_tipo_token(nome, self.tokenLido[2], self.tokenLido[3])
        self.consome(TOKEN.IN)
        texto = f'for {nome} in '
        colunaTipo = self.tokenLido[3]
        (tipoRange, lexema) = self.range()
        if tipo[0] != tipoRange[0] or not tipoRange[1]:
            raise Exception(f'Parâmetros inválidos. "FOR", era esperado "{TOKEN.msg(tipoRange[0])}" mas veio "{TOKEN.msg(tipo[0])}". Linha: {self.tokenLido[2]}, coluna: {colunaTipo}')
        self.consome(TOKEN.DO)
        self.semantico.gera(indentacao, texto + lexema + ':\n')
        self.com(indentacao+1)

    # <range> -> <lista> | range ( <exp> , <exp> <opcRange> )
    def range(self):
        if self.tokenLido[0] == TOKEN.IDENT:
            return self.lista()
        else:
            self.consome(TOKEN.RANGE)
            self.consome(TOKEN.ABRE_PARENTESES)
            texto = 'range('
            # TODO: Não pode ser string
            (_, texto1) = self.exp()
            self.consome(TOKEN.VIRGULA)
            (_, texto2) = self.exp()
            (_, texto3) = self.opcRange()
            self.consome(TOKEN.FECHA_PARENTESES)
            if texto3:
                texto += f'{texto1}, {texto2}, {texto3})'
            else:
                texto += f'{texto1}, {texto2})'
            return ((TOKEN.INT, True), texto)

    # <lista> -> ident <opcIndice> | [ <elemLista> ]
    def lista(self):
        if self.tokenLido[0] == TOKEN.IDENT:
            nome = self.tokenLido[1]
            self.consome(TOKEN.IDENT)
            self.semantico.verifica_declaracao(nome)
            tipo = self.semantico.obter_tipo_token(nome, self.tokenLido[2], self.tokenLido[3])
            indice = self.opcIndice()
            return (tipo, nome + indice)
        else:
            self.consome(TOKEN.ABRE_COLCHETES)
            (tipoPrimeiroElem, lexema) = self.elemLista()
            self.consome(TOKEN.FECHA_COLCHETES)
            return (tipoPrimeiroElem, lexema)


    # <elemLista> -> LAMBDA | <elem> <restoElemLista>
    def elemLista(self):
        elem = [TOKEN.INTVAL, TOKEN.FLOATVAL, TOKEN.STRVAL, TOKEN.IDENT]
        if self.tokenLido[0] in elem:
            (tipoPrimeiroElem, lexema) = self.elem()
            self.restoElemLista()
            return (tipoPrimeiroElem, lexema)
        else:
            pass

    # <restoElemLista> -> LAMBDA | , <elem> <restoElemLista>
    def restoElemLista(self):
        if self.tokenLido[0] == TOKEN.VIRGULA:
            self.consome(TOKEN.VIRGULA)
            self.elem()
            self.restoElemLista()
        else:
            pass

    # <elem> -> intVal | floatVal | strVal | ident
    def elem(self):
        lexema = self.tokenLido[1]
        if self.tokenLido[0] == TOKEN.INTVAL:
            self.consome(TOKEN.INTVAL)
            return ((TOKEN.INTVAL, False), lexema)
        elif self.tokenLido[0] == TOKEN.FLOATVAL:
            self.consome(TOKEN.FLOATVAL)
            return ((TOKEN.FLOATVAL, False), lexema)
        elif self.tokenLido[0] == TOKEN.STRVAL:
            self.consome(TOKEN.STRVAL)
            return ((TOKEN.STRVAL, False), lexema)
        else:
            nome = self.tokenLido[1]
            self.consome(TOKEN.IDENT)
            (tipoPrimeiroElem, _) = self.semantico.obter_tipo_token(nome, self.tokenLido[2], self.tokenLido[3])
            return (tipoPrimeiroElem, nome)

    # <opcRange> -> , <exp> | LAMBDA
    def opcRange(self):
        if self.tokenLido[0] == TOKEN.VIRGULA:
            self.consome(TOKEN.VIRGULA)
            return self.exp()
        else:
            return (None, '')
    
    # <calculo> -> LAMBDA | <com><calculo>
    def calculo(self, indentacao = 0):
        com = [TOKEN.IDENT, TOKEN.IF, TOKEN.READ, TOKEN.WRITE, TOKEN.ABRE_CHAVES, TOKEN.FOR, TOKEN.WHILE, TOKEN.RETURN]
        entrou = False
        while self.tokenLido[0] in com:
            self.com(indentacao)
            entrou = True
        
        if not entrou:
            pass 

    # <com> -> <atrib>|<if>|<leitura>|<escrita>|<bloco>|<for>|<while>|<retorna>|<call>
    def com(self, indentacao = 0): #FIXME: Remover 0 depois de validar todos
        if self.tokenLido[0] == TOKEN.IDENT:
            nome = self.tokenLido[1]
            (tipo, _) = self.semantico.obter_tipo_token(nome, self.tokenLido[2], self.tokenLido[3])
            if tipo == TOKEN.FUNCTION:
                self.call()
                self.consome(TOKEN.PONTO_VIRGULA)
            else:
                self.atrib(indentacao)
        elif self.tokenLido[0] == TOKEN.IF:
            self._if_(indentacao)
        elif self.tokenLido[0] == TOKEN.READ:
            self.leitura()
        elif self.tokenLido[0] == TOKEN.WRITE:
            self.escrita(indentacao)
        elif self.tokenLido[0] == TOKEN.ABRE_CHAVES:
            self.bloco(indentacao)
        elif self.tokenLido[0] == TOKEN.FOR:
            self._for_(indentacao)
        elif self.tokenLido[0] == TOKEN.WHILE:
            self._while_()
        else:
            self.retorna(indentacao)

    # <atrib> -> ident <opcIndice> = <exp> ;
    def atrib(self, indentacao):
        nome = self.tokenLido[1]
        self.consome(TOKEN.IDENT)
        self.semantico.verifica_declaracao(nome)
        textoIndice = nome + self.opcIndice()
        textoIndice += ' = '
        self.consome(TOKEN.ATRIBUICAO)
        (_, lexema) = self.exp()
        textoIndice += lexema + '\n'
        self.consome(TOKEN.PONTO_VIRGULA)
        self.semantico.gera(indentacao, textoIndice)


    # <if> ->  if ( <exp> ) then <com> <else_opc>
    def _if_(self, indentacao = 0):
        self.consome(TOKEN.IF)
        self.consome(TOKEN.ABRE_PARENTESES)
        (_, lexema) = self.exp()
        self.consome(TOKEN.FECHA_PARENTESES)
        self.consome(TOKEN.THEN)
        texto = f'if ({lexema}):\n'
        self.semantico.gera(indentacao, texto)
        self.com(indentacao+1)
        self.else_opc()

    # <else_opc> -> LAMBDA | else <com> 
    def else_opc(self):
        if self.tokenLido[0] == TOKEN.ELSE:
            self.consome(TOKEN.ELSE)
            self.com()
        else:
            pass

    # <leitura> -> read ( strVal , ident ) ;
    def leitura(self):
        self.consome(TOKEN.READ)
        self.consome(TOKEN.ABRE_PARENTESES)
        self.consome(TOKEN.STRVAL)
        self.consome(TOKEN.VIRGULA)
        self.consome(TOKEN.IDENT)
        self.consome(TOKEN.FECHA_PARENTESES)
        self.consome(TOKEN.PONTO_VIRGULA)

    # <escrita> -> write ( <lista_outs> ) ;
    def escrita(self, indentacao = 0):
        self.consome(TOKEN.WRITE)
        self.consome(TOKEN.ABRE_PARENTESES)
        (_, lexemas) = self.lista_outs()
        self.consome(TOKEN.FECHA_PARENTESES)
        self.consome(TOKEN.PONTO_VIRGULA)
        texto = f'print({lexemas})\n'
        self.semantico.gera(indentacao, texto)

    # <lista_outs> -> <out> <restoLista_outs>
    def lista_outs(self):
        parametros = list()
        (parametro, lexemas) = self.out()
        parametros.append(parametro)
        lexemas += self.restoLista_outs(parametros)
        return (parametros, lexemas)

    # <restoLista_outs> -> LAMBDA | , <out> <restoLista_outs>
    def restoLista_outs(self, parametros: list):
        if self.tokenLido[0] == TOKEN.VIRGULA:
            lexemas = ', '
            self.consome(TOKEN.VIRGULA)
            (parametro, lexema) = self.out()
            parametros.append(parametro)
            lexemas += lexema
            return lexemas + self.restoLista_outs(parametros)
        else:
            return ''

    # <out> -> <folha>
    def out(self):
        return self.folha()

    # <bloco> -> { <calculo> }
    def bloco(self, indentacao = 0):
        self.consome(TOKEN.ABRE_CHAVES)
        self.calculo(indentacao)
        self.consome(TOKEN.FECHA_CHAVES)
        
    # <exp> -> <disj>
    def exp(self, operacao: list = list()):
        return self.disj(operacao)
            
    # <disj> -> <conj> <restoDisj>
    def disj(self, operacao: list):
        (tipo, lexema) = self.conj(operacao) 
        lexema += self.restoDisj(operacao)
        return (tipo, lexema)

    # <restoDisj> -> LAMBDA | or <conj> <restoDisj>
    def restoDisj(self, operacao: list):
        if self.tokenLido[0] == TOKEN.OR:
            self.consome(TOKEN.OR)
            operacao.append(TOKEN.OR)
            (_, lexema) = self.conj(operacao)
            lexema = 'or ' + lexema
            return lexema + self.restoDisj(operacao)
        else:
            return ''

    # <conj> -> <nao> <restoConj>
    def conj(self, operacao: list):
        (tipo, lexema) = self.nao(operacao)
        lexema += self.restoConj(operacao)
        return (tipo, lexema)

    # <restoConj> -> LAMBDA | and <nao> <restoConj>
    def restoConj(self, operacao: list):
        if self.tokenLido[0] == TOKEN.AND:
            self.consome(TOKEN.AND)
            operacao.append(TOKEN.AND)
            (_, lexema) = self.nao(operacao)
            lexema = 'and ' + lexema
            return lexema + self.restoConj(operacao)
        else:
            return ''

    # <nao> -> not <nao> | <rel>
    def nao(self, operacao: list):
        if self.tokenLido[0] == TOKEN.NOT:
            self.consome(TOKEN.NOT)
            operacao.append(TOKEN.NOT)
            (tipo, lexema) = self.nao(operacao)
            return (tipo, 'not ' + lexema)
        else:
            return self.rel(operacao)

    # <rel> -> <soma> <restoRel>
    def rel(self, operacao: list):
        (tipo, lexema) = self.soma(operacao)
        lexema += self.restoRel(operacao)
        return (tipo, lexema)

    # <restoRel> -> LAMBDA | oprel <soma>
    def restoRel(self, operacao: list):
        if self.tokenLido[0] in TOKEN.oprel():
            operacao.append(self.tokenLido[0])
            oprel = f' {self.tokenLido[1]} '
            self.consome(self.tokenLido[0])
            (_, lexema) = self.soma(operacao)
            return oprel + lexema
        else:
            return ''

    # <soma> -> <mult> <restoSoma>
    def soma(self, operacao: list):
        (tipo, lexema) = self.mult(operacao)
        lexema += self.restoSoma(operacao)
        return (tipo, lexema)

    # <restoSoma> -> LAMBDA | + <mult> <restoSoma> | - <mult> <restoSoma>
    def restoSoma(self, operacao: list):
        if self.tokenLido[0] == TOKEN.SOMA:
            self.consome(TOKEN.SOMA)
            operacao.append(TOKEN.SOMA)
            (_, lexema) = self.mult(operacao)
            texto = '+' + lexema
            return texto + self.restoSoma(operacao)
        elif self.tokenLido[0] == TOKEN.SUBTRACAO:
            self.consome(TOKEN.SUBTRACAO)
            operacao.append(TOKEN.SUBTRACAO)
            (_, lexema) = self.mult(operacao)
            texto = '-' + lexema
            return texto + self.restoSoma(operacao)
        else:
            return ''

    # <mult> -> <uno> <restoMult>
    def mult(self, operacao: list):
        (tipo, lexema) = self.uno(operacao)
        lexema += self.restoMult(operacao)
        return (tipo, lexema)

    # <restoMult> -> LAMBDA | / <uno> <restoMult> | * <uno> <restoMult> | % <uno> 
    def restoMult(self, operacao: list):
        if self.tokenLido[0] == TOKEN.DIVISAO:
            self.consome(TOKEN.DIVISAO)
            operacao.append(TOKEN.DIVISAO)
            (_, lexema) = self.uno(operacao)
            texto = '/' + lexema
            return texto + self.restoMult(operacao)
        elif self.tokenLido[0] == TOKEN.MULTIPLICACAO:
            self.consome(TOKEN.MULTIPLICACAO)
            operacao.append(TOKEN.MULTIPLICACAO)
            (_, lexema) = self.uno(operacao)
            texto = '*' + lexema
            return texto + self.restoMult(operacao)
        elif self.tokenLido[0] == TOKEN.MOD:
            self.consome(TOKEN.MOD)
            operacao.append(TOKEN.MOD)
            (_, lexema) = self.uno(operacao)
            texto = '%' + lexema
            return texto + self.restoMult(operacao)
        else:
            return ''

    # <uno> -> + <uno> | - <uno> | <folha>
    def uno(self, operacao: list):
        if self.tokenLido[0] == TOKEN.SOMA:
            self.consome(TOKEN.SOMA)
            operacao.append((TOKEN.SOMA))
            (tipo, lexema) = self.uno(operacao)
            return (tipo, '+' + lexema)
        elif self.tokenLido[0] == TOKEN.SUBTRACAO:
            self.consome(TOKEN.SUBTRACAO)
            operacao.append((TOKEN.SUBTRACAO))
            (tipo, lexema) = self.uno(operacao)
            return (tipo, '-' + lexema)
        else:
            (tipo, lexema) = self.folha()
            operacao.append(tipo)
            return (tipo, lexema)
            
    # <folha> -> intVal | floatVal | strVal | <call> | <lista> | ( <exp> ) 
    def folha(self):
        lexema = self.tokenLido[1]
        if self.tokenLido[0] == TOKEN.INTVAL:
            self.consome(TOKEN.INTVAL)
            return ((TOKEN.INT, False), lexema)
        elif self.tokenLido[0] == TOKEN.FLOATVAL:
            self.consome(TOKEN.FLOATVAL)
            return ((TOKEN.FLOAT, False), lexema)
        elif self.tokenLido[0] == TOKEN.STRVAL:
            self.consome(TOKEN.STRVAL)
            return ((TOKEN.STRING, False), lexema)
        elif self.tokenLido[0] == TOKEN.ABRE_COLCHETES:
            return self.lista()
        elif self.tokenLido[0] == TOKEN.ABRE_PARENTESES:
            self.consome(TOKEN.ABRE_PARENTESES)
            tipo = self.exp() # !!!! IMPLEMENTAR RETORNO
            self.consome(TOKEN.FECHA_PARENTESES)
            return tipo
        elif self.tokenLido[0] == TOKEN.IDENT:
            nome = self.tokenLido[1]
            (tipo, _) = self.semantico.obter_tipo_token(nome, self.tokenLido[2], self.tokenLido[3])
            if tipo == TOKEN.FUNCTION:
                return self.call()
            else:
                return self.lista()
        elif self.tokenLido[0] == TOKEN.TRUE:
            self.consome(TOKEN.TRUE)
            return ((TOKEN.TRUE, False), lexema)
        else:
            self.semantico.erro_semantico(self.tokenLido, f"{self.tokenLido[1]}")

    # <call> -> ident ( <lista_outs_opc> )
    def call(self):
        nome = self.tokenLido[1]
        self.consome(TOKEN.IDENT)
        self.consome(TOKEN.ABRE_PARENTESES)
        (_, params) = self.semantico.obter_tipo_token(nome, self.tokenLido[2], self.tokenLido[3])
        # params = () 
        (paramsPassado, lexemas) = self.lista_outs_opc(params)

        if len(params[:-1]) != len(paramsPassado):
            raise Exception(f'Parâmetros inválidos. Função: "{nome}", linha: {self.tokenLido[2]}, coluna: {self.tokenLido[3]}')
        for i in range(len(params[:-1])):
            param = params[i]
            if param[1] == paramsPassado[i]:
                continue
            elif param[1][0] is None and param[1][1] == paramsPassado[i][1]:
                continue
            elif param[1][0] == TOKEN.FLOAT and (paramsPassado[i][0] == TOKEN.INT and param[1][1] == paramsPassado[i][1]):
                continue
            else:
                raise Exception(f'Parâmetros inválidos. Função: "{nome}", linha: {self.tokenLido[2]}, coluna: {self.tokenLido[3]}')


        self.consome(TOKEN.FECHA_PARENTESES)
        (_, tipo) = params[-1]
        texto = f'{nome}({lexemas})'
        return (tipo, texto)

    # <lista_outs_opc> -> <lista_outs> | LAMBDA
    def lista_outs_opc(self, params): #FIXME: Verificar argumento params
        folha = [
            TOKEN.INTVAL,
            TOKEN.FLOATVAL,
            TOKEN.STRVAL,
            TOKEN.IDENT,
            TOKEN.ABRE_PARENTESES
        ]
        if self.tokenLido[0] in folha:
            return self.lista_outs()
        else:
            ((None, (None, None)), '')

    # <opcIndice> -> LAMBDA | [ <exp> <restoElem> ]
    def opcIndice(self):
        if self.tokenLido[0] == TOKEN.ABRE_COLCHETES:
            textoIndice = '['
            self.consome(TOKEN.ABRE_COLCHETES)
            (_, lexema) = self.exp()
            textoIndice += lexema
            self.restoElem(textoIndice)
            self.consome(TOKEN.FECHA_COLCHETES)
            return textoIndice + ']'
        else:
            return ''

    # <restoElem> -> LAMBDA | : <exp>
    def restoElem(self, textoIndice = ''):
        if self.tokenLido[0] == TOKEN.DOIS_PONTOS:
            textoIndice += ':'
            self.consome(TOKEN.DOIS_PONTOS)
            (_, lexema) = self.exp()
            textoIndice += lexema
        else:
            pass