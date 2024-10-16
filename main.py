from fastapi import FastAPI, File, UploadFile
from pydantic import BaseModel
from typing import List
import pdfplumber
import logging
import re

# Configuração do logger
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI()

class Nome(BaseModel):
    nome: str

@app.post("/upload_pdf", response_model=List[Nome])
async def upload_pdf(file: UploadFile = File(...)):
    logger.info("Recebendo arquivo: %s", file.filename)  # Log do nome do arquivo recebido
    content = await file.read()

    # Chame a função de extração
    lista_nomes = extract_names_from_pdf(content)

    logger.info("Processamento do arquivo %s concluído.", file.filename)  # Log após o processamento
    return lista_nomes

def extract_names_from_pdf(pdf_bytes):
    lista_nomes = []
    
    # Salvar os bytes em um arquivo temporário
    temp_file_path = "temp.pdf"
    with open(temp_file_path, "wb") as temp_file:
        temp_file.write(pdf_bytes)

    logger.info("Arquivo temporário criado: %s", temp_file_path)  # Log do arquivo temporário criado

    # Agora abra o arquivo PDF a partir do arquivo temporário
    with pdfplumber.open(temp_file_path) as pdf:
        for page in pdf.pages:
            text = page.extract_text()
            if text:  # Verifica se há texto na página
                # Aqui filtramos as linhas que contêm nomes
                for line in text.split("\n"):
                    logger.info("Linha extraída: %s", line)  # Log para verificar cada linha extraída
                    # Usar regex para capturar nomes no formato "Sobrenome, Nome"
                    # Ignorar o "F" ou "M" no final do nome
                    pattern = re.compile(r'^([A-Za-zÀ-ÿ\s]+,\s[A-Za-zÀ-ÿ\s]+)\s[F|M]')  # Captura o nome sem "F" ou "M"
                    match = pattern.match(line)
                    if match:  # Verifica se há correspondência
                        nome = match.group(1)  # Captura apenas o nome
                        lista_nomes.append({"nome": nome})

    logger.info("Nomes extraídos: %d", len(lista_nomes))  # Log do número de nomes extraídos

    return lista_nomes
