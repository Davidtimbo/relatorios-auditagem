import os
import sys
import time
import logging
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
from reportlab.lib import colors
from reportlab.lib.pagesizes import landscape, A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle
from email.mime.text import MIMEText
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import Paragraph
import shutil

# Configuração do logger
logging.basicConfig(
    filename='****/auditagem.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Lista de emails para correspondência (anonimizada)
emails = {
    '****@****.com': 'usuario1',
    '****@****.com': 'usuario2',
    '****@****.com': 'usuario3',
    # ...
}

# Função para enviar e-mail com PDF
def enviar_email_com_anexo(remetente, assunto, caminho_pdf, destinatario, caminho_txt=None):
    logging.info(f"Enviando e-mail para {destinatario} com o arquivo {os.path.basename(caminho_pdf)}")
    
    msg = MIMEMultipart()
    msg['From'] = remetente
    msg['To'] = destinatario
    msg['Subject'] = assunto

    corpo_html = """
    <html>
    <body>
       <h2>Comparativo com base nas contas pagas no mês anterior</h2>
    </body>
    </html>
    """
    msg.attach(MIMEText(corpo_html, 'html'))

    # Anexar o arquivo PDF
    try:
        with open(caminho_pdf, "rb") as f:
            parte = MIMEBase('application', 'octet-stream')
            parte.set_payload(f.read())
            encoders.encode_base64(parte)
            parte.add_header('Content-Disposition', f'attachment; filename={os.path.basename(caminho_pdf)}')
            msg.attach(parte)
    except Exception as e:
        logging.error(f"Erro ao anexar o arquivo PDF: {e}")
        return

    if caminho_txt:
        try:
            with open(caminho_txt, "rb") as f:
                parte_txt = MIMEBase('application', 'octet-stream')
                parte_txt.set_payload(f.read())
                encoders.encode_base64(parte_txt)
                parte_txt.add_header('Content-Disposition', f'attachment; filename={os.path.basename(caminho_txt)}')
                msg.attach(parte_txt)
        except Exception as e:
            logging.error(f"Erro ao anexar o arquivo TXT: {e}")
            return

    comando_sendemail = (
        f"sendEmail -o tls=no -f {remetente} -t {destinatario} -u \"{assunto}\" "
        f"-m \"{corpo_html}\" -s **** -a \"{caminho_pdf}\""
    )
    
    if caminho_txt:
        comando_sendemail += f" -a \"{caminho_txt}\""

    resultado = os.system(comando_sendemail)
    
    if resultado != 0:
        logging.error(f"Falha ao enviar e-mail para {destinatario}")
    else:
        logging.info(f"E-mail enviado com sucesso para {destinatario}")


# Função para gerar PDF estilizado
def gerar_pdf_stilizado(dados, caminho_pdf, largura=landscape(A4)):
    logging.info(f"Gerando PDF {os.path.basename(caminho_pdf)}")

    pdf = SimpleDocTemplate(caminho_pdf, pagesize=largura)
    elementos = []
    estilos = getSampleStyleSheet()
    estilo_titulo = estilos['Title']
    titulo = Paragraph("CONTAS A PAGAR", estilo_titulo)
    elementos.append(titulo)

    tabela = Table(dados)
    tabela.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black),
    ]))
    elementos.append(tabela)
    pdf.build(elementos)


# Função para processar arquivos TXT com padrão "CONTAZZZ"
def processar_arquivo_e_gerar_pdfs(diretorio_txt, largura=landscape(A4)):
    logging.info(f"Processando arquivos no diretório {diretorio_txt}")

    remetente = "****@****.com"
    linhas_por_pessoa = {}

    arquivos_txt = [f for f in os.listdir(diretorio_txt) if f.endswith('.txt') and "CONTAZZZ" in f]
    if len(arquivos_txt) == 0:
        logging.warning("Nenhum arquivo TXT encontrado.")
        return

    for arquivo in arquivos_txt:
        file_path = os.path.join(diretorio_txt, arquivo)
        logging.info(f"Arquivo TXT encontrado: {file_path}")

        nome_arquivo = os.path.basename(file_path)
        data_auditagem = nome_arquivo.split('CONTAZZZ')[-1].split('.')[0]
        data_formatada = f"{data_auditagem[:2]}/{data_auditagem[2:4]}/{data_auditagem[4:]}"

        with open(file_path, 'r') as f:
            for linha in f:
                partes = linha.strip().split(';')
                if len(partes) > 1:
                    nome = partes[0].strip()
                    for email, nome_busca in emails.items():
                        if nome == nome_busca:
                            if email not in linhas_por_pessoa:
                                linhas_por_pessoa[email] = []
                            linhas_por_pessoa[email].append(partes)

        cabecalho = [
            "Consultor", "Código", "Local", "H.Padrão", "Descrição", 
            "Pgto. Anterior"
        ]

        # Gerar PDFs individuais
        for email, linhas in linhas_por_pessoa.items():
            dados = [cabecalho] + [linha[:-1] for linha in linhas]
            if len(dados) > 1:
                caminho_pdf = f"/tmp/auditagem_{email.split('@')[0]}.pdf"
                gerar_pdf_stilizado(dados, caminho_pdf, largura)
                assunto = f"Auditagens - {data_formatada} - {email.split('@')[0]}"
                enviar_email_com_anexo(remetente, assunto, caminho_pdf, email)
                time.sleep(5)

        # Gerar PDF completo
        dados_completo = [cabecalho] + [linha[:-1] for linhas in linhas_por_pessoa.values() for linha in linhas]
        caminho_pdf_completo = "/tmp/auditagem_completa.pdf"
        gerar_pdf_stilizado(dados_completo, caminho_pdf_completo, largura)

        assunto_completo = f"Auditagem Completa - {data_formatada}"
        destinatarios_completos = [
            "****@****.com",
            "****@****.com"
        ]

        for destinatario in destinatarios_completos:
            enviar_email_com_anexo(remetente, assunto_completo, caminho_pdf_completo, destinatario)

        enviar_email_com_anexo(remetente, f"{assunto_completo} + TXT", caminho_pdf_completo, "****@****.com", caminho_txt=file_path)

        caminho_backup = "****/.backup"
        if not os.path.exists(caminho_backup):
            os.makedirs(caminho_backup)
        shutil.move(file_path, os.path.join(caminho_backup, os.path.basename(file_path)))
        print(f"Arquivo {file_path} movido para {caminho_backup}")


# Diretório dos arquivos TXT
diretorio_txt = '****'

# Execução
processar_arquivo_e_gerar_pdfs(diretorio_txt, largura=landscape((700, 600)))
