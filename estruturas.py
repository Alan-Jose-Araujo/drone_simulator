# --- START OF FILE estruturas.py ---

class Node:
    """
    Nó de uma lista encadeada. Armazena os dados e a referência para o próximo nó.
    """
    def __init__(self, data):
        self.data = data  # Os dados armazenados (no nosso caso, um objeto DataPoint)
        self.next = None  # Ponteiro para o próximo nó


class LinkedList:
    """
    Implementação de uma lista simplesmente encadeada.
    NÃO utiliza recursos de listas prontas do Python para seu funcionamento interno.
    """
    def __init__(self):
        self.head = None
        self.count = 0

    def append(self, data):
        """Adiciona um elemento ao final da lista."""
        new_node = Node(data)
        if self.head is None:
            self.head = new_node
        else:
            current = self.head
            while current.next:
                current = current.next
            current.next = new_node
        self.count += 1

    def __len__(self):
        """Retorna o número de elementos na lista."""
        return self.count

    def __iter__(self):
        """Permite a iteração sobre a lista (ex: for item in list)."""
        current = self.head
        while current:
            yield current.data
            current = current.next

    def is_empty(self):
        """Verifica se a lista está vazia."""
        return self.head is None

# --- END OF FILE estruturas.py ---