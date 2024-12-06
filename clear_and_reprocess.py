from pdf_processor import PDFProcessor
import os
from dotenv import load_dotenv

load_dotenv()

def main():
    print("Iniciando limpeza e reprocessamento...")
    pdf_processor = PDFProcessor("pdfs")
    
    # Limpa todos os dados
    print("\nLimpando base de dados...")
    pdf_processor.clear_supabase_data()
    
    # Remove o arquivo de versão para forçar reprocessamento
    if os.path.exists("pdf_version.json"):
        os.remove("pdf_version.json")
        print("Arquivo de versão removido.")
    
    print("\nBase limpa! Agora você pode rodar o programa principal normalmente.")
    print("Os PDFs serão reprocessados com os novos tamanhos de chunk na próxima execução.")

if __name__ == "__main__":
    main()
