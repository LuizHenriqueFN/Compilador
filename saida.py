# Codigo gerado pelo compilador
class Programa:
    def __init__(self):
        pass

    def sort(self, lista):
        tam = len(lista)
        for topo in range(tam, 1, -1):
            for bolha in range(0, topo-1):
                if (lista[bolha] > lista[bolha+1]):
                    aux = lista[bolha]
                    lista[bolha] = lista[bolha+1]
                    lista[bolha+1] = aux
        return lista

    def imprime(self, lista):
        print("\nLista ordenada: \n")
        for i in lista:
            print(i, "\n")
        print("FIM\n")

    def main(self):
        print("Forneca inteiros para ordenar (0=termina):")
        n = 1
        prompt = num2str(n)+"o: "
