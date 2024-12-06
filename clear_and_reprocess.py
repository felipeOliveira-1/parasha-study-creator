from pdf_processor import PDFProcessor
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

def main():
    print("Iniciando limpeza e reprocessamento...")
    
    # Usa a constante PDF_FOLDER do arquivo main.py
    pdf_processor = PDFProcessor("livros")  # Atualizado para usar o diretório correto
    
    # Limpa todos os dados
    print("\nLimpando base de dados...")
    pdf_processor.clear_supabase_data()
    
    # Remove os arquivos de controle para forçar reprocessamento
    version_files = ["pdf_version.json", "processed_files.json"]
    for file in version_files:
        if os.path.exists(file):
            os.remove(file)
            print(f"Arquivo {file} removido.")
    
    # Força o reprocessamento de todos os arquivos
    print("\nReprocessando todos os arquivos...")
    pdf_processor.create_vector_store()
    
    print("\nProcesso concluído! A base de dados foi atualizada com todos os arquivos.")

if __name__ == "__main__":
    main()
