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
        self.funcao()
        self.restoFuncoes()

    # <restoFuncoes> -> <funcao> <restoFuncoes> | LAMBDA
    def restoFuncoes(self):
        if self.tokenLido[0] == TOKEN.FUNCTION:
            self.funcao()
            self.restoFuncoes()
        else:
            pass

    # <funcao> -> function ident ( <params> ) <tipoResultado> <corpo>
    def funcao(self):
        self.consome(TOKEN.FUNCTION)  # Consome 'function'
        nome = self.tokenLido[1]  # Captura o identificador (nome da função)
        self.consome(TOKEN.IDENT)  # Consome o identificador
        self.consome(TOKEN.ABRE_PARENTESES)  # Consome '('
        args = self.params()  # Chama a produção 'params' para processar os parâmetros
        self.consome(TOKEN.FECHA_PARENTESES)  # Consome ')'
        args.append(self.tipoResultado())  # Obtém o tipo da função (após '->' ou vazio)
        self.semantico.declara(nome, (TOKEN.FUNCTION, args))  # Atualiza com o tipo da função
        self.semantico.entra_escopo()  # Entra no escopo local da função
        for (nome, tipo) in args:
            if nome != 'retorno':
                self.semantico.declara(nome, tipo)
        self.corpo()  # Processa o corpo da função
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
    def corpo(self):
        self.consome(TOKEN.BEGIN)
        self.declaracoes()
        self.calculo()
        self.consome(TOKEN.END)

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
    def retorna(self):
        self.consome(TOKEN.RETURN)
        self.expOpc()
        self.consome(TOKEN.PONTO_VIRGULA)

    # <expOpc> -> LAMBDA | <exp>
    def expOpc(self):
        exp = [TOKEN.NOT, TOKEN.SOMA, TOKEN.SUBTRACAO, TOKEN.INTVAL, TOKEN.FLOATVAL, TOKEN.STRVAL, TOKEN.IDENT, TOKEN.ABRE_PARENTESES]
        if self.tokenLido[0] in exp:
            self.exp()
        else:
            pass

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
    def _for_(self):
        self.consome(TOKEN.FOR)
        nome = self.tokenLido[1]
        self.consome(TOKEN.IDENT)
        tipo = self.semantico.obter_tipo_token(nome, self.tokenLido[2], self.tokenLido[3])
        self.consome(TOKEN.IN)
        colunaTipo = self.tokenLido[3]
        tipoRange = self.range()
        if tipo[0] != tipoRange[0] or not tipoRange[1]:
            raise Exception(f'Parâmetros inválidos. "FOR", era esperado "{TOKEN.msg(tipoRange[0])}" mas veio "{TOKEN.msg(tipo[0])}". Linha: {self.tokenLido[2]}, coluna: {colunaTipo}')
        self.consome(TOKEN.DO)
        self.com()

    # <range> -> <lista> | range ( <exp> , <exp> <opcRange> )
    def range(self):
        if self.tokenLido[0] == TOKEN.IDENT:
            return self.lista()
        else:
            self.consome(TOKEN.RANGE)
            self.consome(TOKEN.ABRE_PARENTESES)
            # TODO: Não pode ser string
            self.exp()
            self.consome(TOKEN.VIRGULA)
            self.exp()
            self.opcRange()
            self.consome(TOKEN.FECHA_PARENTESES)
            return (TOKEN.INT, True)

    # <lista> -> ident <opcIndice> | [ <elemLista> ]
    def lista(self):
        if self.tokenLido[0] == TOKEN.IDENT:
            nome = self.tokenLido[1]
            self.consome(TOKEN.IDENT)
            self.semantico.verifica_declaracao(nome)
            tipo = self.semantico.obter_tipo_token(nome, self.tokenLido[2], self.tokenLido[3])
            self.opcIndice()
            return tipo
        else:
            self.consome(TOKEN.ABRE_COLCHETES)
            tipoPrimeiroElem = self.elemLista()
            self.consome(TOKEN.FECHA_COLCHETES)
            return tipoPrimeiroElem


    # <elemLista> -> LAMBDA | <elem> <restoElemLista>
    def elemLista(self):
        elem = [TOKEN.INTVAL, TOKEN.FLOATVAL, TOKEN.STRVAL, TOKEN.IDENT]
        if self.tokenLido[0] in elem:
            tipoPrimeiroElem = self.elem()
            self.restoElemLista()
            return tipoPrimeiroElem
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
        if self.tokenLido[0] == TOKEN.INTVAL:
            self.consome(TOKEN.INTVAL)
            return (TOKEN.INTVAL, False)
        elif self.tokenLido[0] == TOKEN.FLOATVAL:
            self.consome(TOKEN.FLOATVAL)
            return (TOKEN.FLOATVAL, False)
        elif self.tokenLido[0] == TOKEN.STRVAL:
            self.consome(TOKEN.STRVAL)
            return (TOKEN.STRVAL, False)
        else:
            nome = self.tokenLido[1]
            self.consome(TOKEN.IDENT)
            (tipoPrimeiroElem, _) = self.semantico.obter_tipo_token(nome, self.tokenLido[2], self.tokenLido[3])
            return tipoPrimeiroElem

    # <opcRange> -> , <exp> | LAMBDA
    def opcRange(self):
        if self.tokenLido[0] == TOKEN.VIRGULA:
            self.consome(TOKEN.VIRGULA)
            self.exp()
        else:
            pass
    
    # <calculo> -> LAMBDA | <com><calculo>
    def calculo(self):
        com = [TOKEN.IDENT, TOKEN.IF, TOKEN.READ, TOKEN.WRITE, TOKEN.ABRE_CHAVES, TOKEN.FOR, TOKEN.WHILE, TOKEN.RETURN]
        entrou = False
        while self.tokenLido[0] in com:
            self.com()
            entrou = True
        
        if not entrou:
            pass 

    # <com> -> <atrib>|<if>|<leitura>|<escrita>|<bloco>|<for>|<while>|<retorna>|<call>
    def com(self):
        if self.tokenLido[0] == TOKEN.IDENT:
            nome = self.tokenLido[1]
            (tipo, _) = self.semantico.obter_tipo_token(nome, self.tokenLido[2], self.tokenLido[3])
            if tipo == TOKEN.FUNCTION:
                self.call()
                self.consome(TOKEN.PONTO_VIRGULA)
            else:
                self.atrib()
        elif self.tokenLido[0] == TOKEN.IF:
            self._if_()
        elif self.tokenLido[0] == TOKEN.READ:
            self.leitura()
        elif self.tokenLido[0] == TOKEN.WRITE:
            self.escrita()
        elif self.tokenLido[0] == TOKEN.ABRE_CHAVES:
            self.bloco()
        elif self.tokenLido[0] == TOKEN.FOR:
            self._for_()
        elif self.tokenLido[0] == TOKEN.WHILE:
            self._while_()
        else:
            self.retorna()

    # <atrib> -> ident <opcIndice> = <exp> ;
    def atrib(self):
        nome = self.tokenLido[1]
        self.consome(TOKEN.IDENT)
        self.semantico.verifica_declaracao(nome)
        self.opcIndice()
        self.consome(TOKEN.ATRIBUICAO)
        self.exp()
        self.consome(TOKEN.PONTO_VIRGULA)


    # <if> ->  if ( <exp> ) then <com> <else_opc>
    def _if_(self):
        self.consome(TOKEN.IF)
        self.consome(TOKEN.ABRE_PARENTESES)
        self.exp()
        self.consome(TOKEN.FECHA_PARENTESES)
        self.consome(TOKEN.THEN)
        self.com()
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
    def escrita(self):
        self.consome(TOKEN.WRITE)
        self.consome(TOKEN.ABRE_PARENTESES)
        self.lista_outs()
        self.consome(TOKEN.FECHA_PARENTESES)
        self.consome(TOKEN.PONTO_VIRGULA)

    # <lista_outs> -> <out> <restoLista_outs>
    def lista_outs(self):
        parametros = list()
        parametros.append(self.out())
        self.restoLista_outs(parametros)
        return parametros

    # <restoLista_outs> -> LAMBDA | , <out> <restoLista_outs>
    def restoLista_outs(self, parametros: list):
        if self.tokenLido[0] == TOKEN.VIRGULA:
            self.consome(TOKEN.VIRGULA)
            parametros.append(self.out())
            self.restoLista_outs(parametros)
        else:
            pass

    # <out> -> <folha>
    def out(self):
        return self.folha()

    # <bloco> -> { <calculo> }
    def bloco(self):
        self.consome(TOKEN.ABRE_CHAVES)
        self.calculo()
        self.consome(TOKEN.FECHA_CHAVES)
        
    # <exp> -> <disj>
    def exp(self, operacao: list = list()):
        return self.disj(operacao)
            
    # <disj> -> <conj> <restoDisj>
    def disj(self, operacao: list):
        aux = self.conj(operacao) 
        self.restoDisj(operacao)
        return aux

    # <restoDisj> -> LAMBDA | or <conj> <restoDisj>
    def restoDisj(self, operacao: list):
        if self.tokenLido[0] == TOKEN.OR:
            self.consome(TOKEN.OR)
            operacao.append(TOKEN.OR)
            self.conj(operacao)
            self.restoDisj(operacao)
        else:
            pass

    # <conj> -> <nao> <restoConj>
    def conj(self, operacao: list):
        aux = self.nao(operacao)
        self.restoConj(operacao)
        return aux

    # <restoConj> -> LAMBDA | and <nao> <restoConj>
    def restoConj(self, operacao: list):
        if self.tokenLido[0] == TOKEN.AND:
            self.consome(TOKEN.AND)
            operacao.append(TOKEN.AND)
            self.nao(operacao)
            self.restoConj(operacao)
        else:
            pass

    # <nao> -> not <nao> | <rel>
    def nao(self, operacao: list):
        if self.tokenLido[0] == TOKEN.NOT:
            self.consome(TOKEN.NOT)
            operacao.append(TOKEN.NOT)
            self.nao(operacao)
        else:
            return self.rel(operacao)

    # <rel> -> <soma> <restoRel>
    def rel(self, operacao: list):
        aux = self.soma(operacao)
        self.restoRel(operacao)
        return aux

    # <restoRel> -> LAMBDA | oprel <soma>
    def restoRel(self, operacao: list):
        if self.tokenLido[0] in TOKEN.oprel():
            operacao.append(self.tokenLido[0])
            self.consome(self.tokenLido[0])
            self.soma(operacao)
        else:
            pass

    # <soma> -> <mult> <restoSoma>
    def soma(self, operacao: list):
        tipo = self.mult(operacao)
        self.restoSoma(operacao)
        return tipo

    # <restoSoma> -> LAMBDA | + <mult> <restoSoma> | - <mult> <restoSoma>
    def restoSoma(self, operacao: list):
        if self.tokenLido[0] == TOKEN.SOMA:
            self.consome(TOKEN.SOMA)
            operacao.append(TOKEN.SOMA)
            self.mult(operacao)
            self.restoSoma(operacao)
        elif self.tokenLido[0] == TOKEN.SUBTRACAO:
            self.consome(TOKEN.SUBTRACAO)
            operacao.append(TOKEN.SUBTRACAO)
            self.mult(operacao)
            self.restoSoma(operacao)
        else:
            pass

    # <mult> -> <uno> <restoMult>
    def mult(self, operacao: list):
        self.uno(operacao)
        self.restoMult(operacao)
        return operacao # FIXME: Remover

    # <restoMult> -> LAMBDA | / <uno> <restoMult> | * <uno> <restoMult> | % <uno> 
    def restoMult(self, operacao: list):
        if self.tokenLido[0] == TOKEN.DIVISAO:
            self.consome(TOKEN.DIVISAO)
            operacao.append(TOKEN.DIVISAO)
            self.uno(operacao)
            self.restoMult(operacao)
        elif self.tokenLido[0] == TOKEN.MULTIPLICACAO:
            self.consome(TOKEN.MULTIPLICACAO)
            operacao.append(TOKEN.MULTIPLICACAO)
            self.uno(operacao)
            self.restoMult(operacao)
        elif self.tokenLido[0] == TOKEN.MOD:
            self.consome(TOKEN.MOD)
            operacao.append(TOKEN.MOD)
            self.uno()
            self.restoMult(operacao)
        else:
            pass

    # <uno> -> + <uno> | - <uno> | <folha>
    def uno(self, operacao: list):
        if self.tokenLido[0] == TOKEN.SOMA:
            self.consome(TOKEN.SOMA)
            operacao.append((TOKEN.SOMA))
            return self.uno(operacao)
        elif self.tokenLido[0] == TOKEN.SUBTRACAO:
            self.consome(TOKEN.SUBTRACAO)
            operacao.append((TOKEN.SUBTRACAO))
            return self.uno(operacao)
        else:
            tipo = self.folha()
            operacao.append(tipo)
            return tipo
            
    # <folha> -> intVal | floatVal | strVal | <call> | <lista> | ( <exp> ) 
    def folha(self):
        if self.tokenLido[0] == TOKEN.INTVAL:
            self.consome(TOKEN.INTVAL)
            return (TOKEN.INT, False)
        elif self.tokenLido[0] == TOKEN.FLOATVAL:
            self.consome(TOKEN.FLOATVAL)
            return (TOKEN.FLOAT, False)
        elif self.tokenLido[0] == TOKEN.STRVAL:
            self.consome(TOKEN.STRVAL)
            return (TOKEN.STRING, False)
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
            return (TOKEN.TRUE, False)
        else:
            self.semantico.erro_semantico(self.tokenLido, f"{self.tokenLido[1]}")

    # <call> -> ident ( <lista_outs_opc> )
    def call(self):
        nome = self.tokenLido[1]
        self.consome(TOKEN.IDENT)
        self.consome(TOKEN.ABRE_PARENTESES)
        (_, params) = self.semantico.obter_tipo_token(nome, self.tokenLido[2], self.tokenLido[3])
        # params = () 
        paramsPassado = self.lista_outs_opc(params)

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
        return tipo

    # <lista_outs_opc> -> <lista_outs> | LAMBDA
    def lista_outs_opc(self, params):
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
            (None, (None, None))

    # <opcIndice> -> LAMBDA | [ <exp> <restoElem> ]
    def opcIndice(self):
        if self.tokenLido[0] == TOKEN.ABRE_COLCHETES:
            self.consome(TOKEN.ABRE_COLCHETES)
            self.exp()
            self.restoElem()
            self.consome(TOKEN.FECHA_COLCHETES)
        else:
            pass

    # <restoElem> -> LAMBDA | : <exp>
    def restoElem(self):
        if self.tokenLido[0] == TOKEN.DOIS_PONTOS:
            self.consome(TOKEN.DOIS_PONTOS)
            self.exp()
        else:
            pass