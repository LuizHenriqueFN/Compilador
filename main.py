from lexico import Lexico
from sintatico import Sintatico

class Tradutor:

    def __init__(self, nomeArq):
        self.nomeArq = nomeArq

    def inicializa(self):
        self.arq = open(self.nomeArq, "r")
        self.lexico = Lexico(self.arq)
        self.sintatico = Sintatico(self.lexico, "./saida.py")

    def traduz(self):
        self.sintatico.traduz()

    def finaliza(self):
        self.arq.close()

# inicia a traducao
if __name__ == '__main__':
    try:
        x = Tradutor('bolha.txt')
        x.inicializa()
        x.traduz()
        x.finaliza()
    except Exception as e:
        print(e)