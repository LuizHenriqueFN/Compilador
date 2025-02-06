def sort(lista):
    tam = len(lista)
    for topo in range(tam, 1, -1):
        for bolha in range(0, topo - 1):
            if lista[bolha] > lista[bolha + 1]:
                aux = lista[bolha]
                lista[bolha] = lista[bolha + 1]
                lista[bolha + 1] = aux
    return lista

def imprime(lista):
    print("\nLista ordenada:")
    for i in lista:
        print(i)
    print("FIM")

def main():
    lista = []
    print("Forneça inteiros para ordenar (0=termina):")
    n = 1
    while True:
        aux = int(input(f"{n}o: "))
        if aux == 0:
            break
        lista.append(aux)
        n += 1
    lista = sort(lista)
    imprime(lista)

if __name__ == "__main__":
    main()