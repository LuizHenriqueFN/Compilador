# Codigo gerado pelo compilador
class Programa:
    def __init__(self):
        pass

    def sort(self, lista):
        bolha = None
        topo = None
        tam = None
        aux = None
        tam = len(lista)
        for topo in range(tam, 1, -1):
            for bolha in range(0, topo - 1):
                if (lista[bolha] > lista[bolha + 1]):
                    aux = lista[bolha]
                    lista[bolha] = lista[bolha + 1]
                    lista[bolha + 1] = aux
        return lista

    def imprime(self, lista):
        i = None
        print("\nLista ordenada: \n")
        for i in lista:
            print(i, "\n")
        print("FIM\n")

    def main(self):
        prompt = ''
        entrada = ''
        n = None
        aux = None
        lista = list()
        print("Forneca inteiros para ordenar (0=termina):")
        n = 1
        prompt = str(n) + "o: "
        lista = []
        while aux != 0:
            entrada = input("msg: ")
            aux = int(entrada)
            lista = lista + [aux]
        lista = self.sort(lista)
        self.imprime(lista)
        return 


if __name__ == "__main__":
    programa = Programa()
    programa.main()
