"""
Servidor de Produção para Windows - Sistema PRÉ SETUP.
Utiliza o Waitress como servidor WSGI multithread de alta performance.
Execute com: python run_server.py
"""
import os
from dotenv import load_dotenv
from waitress import serve
from app import create_app

# Carrega variáveis de ambiente
load_dotenv()

app = create_app()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    print(f"==========================================================")
    print(f"  Iniciando Servidor de Produção (Waitress)")
    print(f"  Escutando em: http://0.0.0.0:{port}")
    print(f"  Sistema pronto para conexões na rede local!")
    print(f"==========================================================")
    
    # Roda o servidor waitress em modo multithread
    serve(app, host='0.0.0.0', port=port, threads=6)
