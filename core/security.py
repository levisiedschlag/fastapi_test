from passlib.context import CryptContext


CRYPTO=CryptContext(schemes=['bcrypt'], deprecated='auto')

def verificar_senha(senha:str, hash_senha:str)->bool:

    return  CRYPTO.verify(senha, hash_senha)


def gerar_hash_senha(senha:str)->str:
    return CRYPTO.hash(senha)