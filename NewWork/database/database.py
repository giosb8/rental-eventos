import pg8000.native

def get_db():
    return pg8000.native.Connection(
        host="localhost",
        port=5433,
        user="postgres",
        password="aluno",
        database="rental_db"
    )
