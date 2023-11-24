from neo4j import GraphDatabase
from neo4j.exceptions import ServiceUnavailable, AuthError

#Aluno: Christopher de Lucas Silveira Freitas

class RedeSocial:

    def __init__(self, uri, usuario, senha):
        self.driver = GraphDatabase.driver(uri, auth=(usuario, senha))
        

    def fechar(self):
        self.driver.close()

    def adicionar_pessoa(self, nome, idade, localizacao):
        with self.driver.session() as sessao:
            return sessao.write_transaction(self._criar_pessoa, nome, idade, localizacao)

    @staticmethod
    def _criar_pessoa(tx, nome, idade, localizacao):
        query = (
            "CREATE (p:Pessoa {nome: $nome, idade: $idade, localizacao: $localizacao}) "
            "RETURN id(p) AS id"
        )
        return tx.run(query, nome=nome, idade=idade, localizacao=localizacao).single()["id"]

    def adicionar_amizade(self, id_pessoa1, id_pessoa2):
        with self.driver.session() as sessao:
            sessao.write_transaction(self._criar_amizade, id_pessoa1, id_pessoa2)

    @staticmethod
    def _criar_amizade(tx, id_pessoa1, id_pessoa2):
        query = (
            "MATCH (a:Pessoa), (b:Pessoa) "
            "WHERE id(a) = $id_pessoa1 AND id(b) = $id_pessoa2 "
            "CREATE (a)-[:AMIGO_DE]->(b) "
            "RETURN a, b"
        )
        tx.run(query, id_pessoa1=id_pessoa1, id_pessoa2=id_pessoa2)

    def listar_pessoas(self):
        with self.driver.session() as sessao:
            pessoas = sessao.read_transaction(self._listar_pessoas)
            if not pessoas:
                print("Não há pessoas cadastradas.")
            return pessoas

    @staticmethod
    def _listar_pessoas(tx):
        query = "MATCH (p:Pessoa) RETURN id(p) AS id, p.nome AS nome"
        return tx.run(query).data()

    def mostrar_amigos(self, id_pessoa):
        with self.driver.session() as sessao:
            amigos = sessao.read_transaction(self._mostrar_amigos, id_pessoa)
            if not amigos:
                print("Esta pessoa não tem amigos cadastrados.")
            return amigos

    @staticmethod
    def _mostrar_amigos(tx, id_pessoa):
        query = (
            "MATCH (p:Pessoa)-[:AMIGO_DE]->(amigo) "
            "WHERE id(p) = $id_pessoa "
            "RETURN id(amigo) AS id, amigo.nome AS nome"
        )
        return tx.run(query, id_pessoa=id_pessoa).data()

    def remover_pessoa(self, id_pessoa):
        with self.driver.session() as sessao:
            sessao.write_transaction(self._remover_pessoa, id_pessoa)

    @staticmethod
    def _remover_pessoa(tx, id_pessoa):
        query = (
            "MATCH (p:Pessoa) "
            "WHERE id(p) = $id_pessoa "
            "DETACH DELETE p"
        )
        tx.run(query, id_pessoa=id_pessoa)

def exibir_menu():
    print("\nMenu da Rede Social:")
    print("1. Adicionar Pessoa")
    print("2. Adicionar Amizade")
    print("3. Listar Pessoas")
    print("4. Mostrar Amigos")
    print("5. Remover Pessoa")
    print("6. Sair")
    escolha = input("Escolha uma opção: ")
    return escolha

def main():
    uri = "neo4j://localhost:7687"
    usuario = "neo4j"
    senha = "PRIVADO"

    try:
        rede_social = RedeSocial(uri, usuario, senha)
    except ServiceUnavailable:
        print("Não foi possível conectar ao banco de dados Neo4j. Verifique se o serviço está ativo.")
        return
    except AuthError:
        print("Falha na autenticação. Verifique seu usuário e senha.")
        return

    while True:
        escolha = exibir_menu()

        if escolha == '1':
            nome = input("Nome da pessoa: ")
            idade = input("Idade da pessoa: ")
            localizacao = input("Localização da pessoa: ")
            try:
                id_pessoa = rede_social.adicionar_pessoa(nome, int(idade), localizacao)
                print(f"Pessoa adicionada com ID: {id_pessoa}")
            except Exception as e:
                print(f"Erro ao adicionar pessoa: {e}")

        elif escolha == '2':
            id_pessoa1 = int(input("ID da primeira pessoa: "))
            id_pessoa2 = int(input("ID da segunda pessoa: "))
            try:
                rede_social.adicionar_amizade(id_pessoa1, id_pessoa2)
                print("Amizade adicionada.")
            except Exception as e:
                print(f"Erro ao adicionar amizade: {e}")

        elif escolha == '3':
            try:
                pessoas = rede_social.listar_pessoas()
                for pessoa in pessoas:
                    print(f"ID: {pessoa['id']}, Nome: {pessoa['nome']}")
            except Exception as e:
                print(f"Erro ao listar pessoas: {e}")

        elif escolha == '4':
            id_pessoa = int(input("ID da pessoa: "))
            try:
                amigos = rede_social.mostrar_amigos(id_pessoa)
                for amigo in amigos:
                    print(f"ID: {amigo['id']}, Nome: {amigo['nome']}")
            except Exception as e:
                print(f"Erro ao mostrar amigos: {e}")

        elif escolha == '5':
            id_pessoa = int(input("ID da pessoa a ser removida: "))
            try:
                rede_social.remover_pessoa(id_pessoa)
                print("Pessoa removida.")
            except Exception as e:
                print(f"Erro ao remover pessoa: {e}")

        elif escolha == '6':
            break

        else:
            print("Opção inválida.")

    rede_social.fechar()

if __name__ == "__main__":
    main()
