import socket
import threading

class Contato:
    def __init__(contato, nome, telefone):
        contato.nome = nome
        contato.telefone = telefone

class PeerToPeer:
    def __init__(self):
        self.peers = set()                      # lista pra armazenar os pares conectados
        self.host = '1.2.3.4'                # endereço IP do dispositivo
        self.port = 9999                            # porta para escutar conexões
        self.contatos = [
            Contato("Izaias", "8698809-7382"),
            Contato("Welsllery", "8062-8922"),
            Contato("DEsconhecido", "0000000")
        ]

    def adicionar_peer(self, peer):             #noa verifica
        self.peers.add(peer)
        print(f"Novo peer adicionado: {peer}")

    def remover_peer(self, peer):
        if peer in self.peers:                  #verifica na lista de peers
            self.peers.remove(peer)
            print(f"Peer removido: {peer}")

    def iniciar_servidor(self):
        servidor = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        servidor.bind((self.host, self.port))
        servidor.listen()

        print(f"Servidor iniciado em {self.host}:{self.port}")

        while True:
            conn, addr = servidor.accept()
            threading.Thread(target=self.lidar_conexao, args=(conn, addr)).start()

    def tratando_conexao(self, conn, addr):
        with conn:
            print(f"Conexão estabelecida com {addr}")
            self.adicionar_peer(addr)

            while True:
                data = conn.recv(1024)
                if not data:
                    break
                mensagem = data.decode()
                if mensagem == 'SOLICITAR_CONTATOS':
                    self.enviar_contatos(conn)
                else:
                    print(f"Mensagem de {addr}: {mensagem}")

            self.remover_peer(addr)
            print(f"Conexão com {addr} encerrada")

    def conectar_peer(self, peer):
        cliente = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            cliente.connect(peer)
            print(f"Conectado a {peer}")
            threading.Thread(target=self.enviar_solicitacao_contatos, args=(cliente,)).start()
            threading.Thread(target=self.receber_mensagens, args=(cliente,)).start()
        except Exception as e:
            print(f"Falha ao conectar a {peer}: {e}")

    def enviar_solicitacao_contatos(self, cliente):
        cliente.sendall('SOLICITAR_CONTATOS'.encode())

    def enviar_contatos(self, conn):
        for contato in self.contatos:
            mensagem = f"Nome: {contato.nome}, Telefone: {contato.telefone}"
            conn.sendall(mensagem.encode())

    def receber_mensagens(self, cliente):
        while True:
            data = cliente.recv(1024)
            if not data:
                break
            print(f"Mensagem do peer {cliente.getpeername()}: {data.decode()}")


if __name__ == '__main__':
    p2p = PeerToPeer()

    # Iniciar servidor em uma thread separada
    threading.Thread(target=p2p.iniciar_servidor).start()

    # Adicionar alguns pares de exemplo
    p2p.conectar_peer(('127.0.0.1', 9998))
    p2p.conectar_peer(('127.0.0.1', 9997))

    # Aguardar entrada do usuário para manter o programa em execução
    input("Pressione Enter para sair...")
