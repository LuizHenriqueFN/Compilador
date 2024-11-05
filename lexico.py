from ttoken import TOKEN


class Lexico:

    def __init__(self, arqFonte):
        self.arqFonte = arqFonte  # objeto file
        self.fonte = self.arqFonte.read()  # string contendo file
        self.tamFonte = len(self.fonte)
        self.indiceFonte = 0
        self.tokenLido = None  # (token, lexema, linha, coluna)
        self.linha = 1  # linha atual no fonte
        self.coluna = 0  # coluna atual no fonte

    def fimDoArquivo(self):
        return self.indiceFonte >= self.tamFonte

    def getchar(self):
        if self.fimDoArquivo():
            return '\0'
        car = self.fonte[self.indiceFonte]
        self.indiceFonte += 1
        if car == '\n':
            self.linha += 1
            # colocar self.coluna = 1 também está funcionando, ver qual dos dois está realmente certo
            self.coluna = 0
        else:
            self.coluna += 1
        return car

    def ungetchar(self, simbolo):
        if simbolo == '\n':
            self.linha -= 1

        if self.indiceFonte > 0:
            self.indiceFonte -= 1

        self.coluna -= 1

    def imprimeToken(self, tokenCorrente):
        (token, lexema, linha, coluna) = tokenCorrente
        msg = TOKEN.msg(token)
        print(f'(tk="{msg}" lex="{lexema}" lin={linha} col={coluna})')

    def getToken(self):
        estado = 1
        simbolo = self.getchar()
        lexema = ''
        while simbolo in ['#', ' ', '\t', '\n']:
            # descarta comentarios (que iniciam com # ate o fim da linha)
            if simbolo == '#':  # DEFINIMOS COMENTÁRIOS COMO #
                simbolo = self.getchar()
                while simbolo != '\n':
                    simbolo = self.getchar()
            # descarta linhas brancas e espaços
            while simbolo in [' ', '\t', '\n']:
                simbolo = self.getchar()
        # aqui vai começar a pegar um token...
        lin = self.linha  # onde inicia o token, para msgs
        col = self.coluna  # onde inicia o token, para msgs
        while (True):
            if estado == 1:
                # inicio do automato
                if simbolo.isalpha():
                    estado = 2  # idents, pal.reservadas
                elif simbolo.isdigit():
                    estado = 3  # numeros
                elif simbolo == '"':
                    estado = 4  # strings
                elif simbolo == "(":
                    return (TOKEN.ABRE_PARENTESES, "(", lin, col)
                elif simbolo == ")":
                    return (TOKEN.FECHA_PARENTESES, ")", lin, col)
                elif simbolo == ",":
                    return (TOKEN.VIRGULA, ",", lin, col)
                elif simbolo == ";":
                    return (TOKEN.PONTO_VIRGULA, ";", lin, col)
                elif simbolo == "+":
                    return (TOKEN.SOMA, "+", lin, col)
                elif simbolo == "-":
                    return (TOKEN.SUBTRACAO, "-", lin, col)
                elif simbolo == "*":
                    return (TOKEN.MULTIPLICACAO, "*", lin, col)
                elif simbolo == "/":
                    return (TOKEN.DIVISAO, "/", lin, col)
                elif simbolo == "{":
                    return (TOKEN.ABRE_CHAVES, "{", lin, col)
                elif simbolo == "}":
                    return (TOKEN.FECHA_CHAVES, "}", lin, col)
                elif simbolo == "<":
                    estado = 5  # < ou <=
                elif simbolo == ">":
                    estado = 6  # > ou >=
                elif simbolo == "=":
                    estado = 7  # = ou ==
                elif simbolo == "!":  # !=
                    estado = 8
                elif simbolo == '\0':
                    return (TOKEN.EOF, '<eof>', lin, col)
                else:
                    lexema += simbolo
                    return (TOKEN.ERRO, lexema, lin, col)

            elif estado == 2:
                # identificadores e palavras reservadas
                if simbolo.isalnum():
                    estado = 2
                else:
                    self.ungetchar(simbolo)
                    token = TOKEN.reservada(lexema)
                    return (token, lexema, lin, col)

            elif estado == 3:
                # numeros
                if simbolo.isdigit():
                    estado = 3
                elif simbolo == '.':
                    estado = 31
                elif simbolo.isalpha():
                    lexema += simbolo
                    return (TOKEN.ERRO, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.NUMERO, lexema, lin, col)
            elif estado == 31:
                # parte real do numero
                if simbolo.isdigit():
                    estado = 32
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.ERRO, lexema, lin, col)
            elif estado == 32:
                # parte real do numero
                if simbolo.isdigit():
                    estado = 32
                elif simbolo.isalpha():
                    lexema += simbolo
                    return (TOKEN.ERRO, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.NUMERO, lexema, lin, col)

            elif estado == 4:
                # strings
                while True:
                    if simbolo == '"':
                        lexema += simbolo
                        return (TOKEN.STRING, lexema, lin, col)
                    if simbolo in ['\n', '\0']:
                        return (TOKEN.ERRO, lexema, lin, col)
                    if simbolo == '\\':  # isso é por causa do python
                        lexema += simbolo
                        simbolo = self.getchar()
                        if simbolo in ['\n', '\0']:
                            return (TOKEN.ERRO, lexema, lin, col)

                    lexema = lexema + simbolo
                    simbolo = self.getchar()

            elif estado == 5:
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.MENOR_IGUAL, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.MENOR, lexema, lin, col)

            elif estado == 6:
                if simbolo == '=':
                    lexema = lexema + simbolo
                    return (TOKEN.MAIOR_IGUAL, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.MAIOR, lexema, lin, col)

            elif estado == 7:
                if simbolo == '=':
                    lexema += simbolo
                    return (TOKEN.IGUAL, lexema, lin, col)
                else:
                    self.ungetchar(simbolo)
                    return (TOKEN.ATRIBUICAO, lexema, lin, col)

            elif estado == 8:
                if simbolo == '=':
                    lexema += simbolo
                    return (TOKEN.DIFERENTE, lexema, lin, col)
                else:  # se o proximo simbolo nao for = , quer dizer que tem um ! solto no código
                    self.ungetchar(simbolo)  # eu volto o "ponteiro" pra posicao que eu encontrei a !
                    return (TOKEN.ERRO, lexema, lin, col)  # retorno o ! dizendo que ele é um erro

            else:
                print('BUG!!!')

            lexema = lexema + simbolo
            simbolo = self.getchar()


# inicia a traducao
if __name__ == '__main__':
    print("Para testar, chame o Tradutor no main.py")