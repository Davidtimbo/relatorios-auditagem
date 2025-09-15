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
    filename='/home/crase/auditagemRelatorio/auditagem.log',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

# Lista de emails para correspondência
emails = {
    'patricia.boing@crasesigma.com.br': 'patricia.boing',
    'cristien.lopes@crasesigma.com.br': 'cristien.lopes',
    'diogo.tavares@crasesigma.com.br': 'diogo.tavares',
    'diogo.colares@crasesigma.com.br': 'diogo.colares',
    'marcos.esposito@crasesigma.com.br': 'marcos.esposito',
    'angela.gimenes@crasesigma.com.br': 'angela.gimenes',
    'alexandre.mendonca@crasesigma.com.br': 'alexandre.mendonca',
    'luis.henrique@crasesigma.com.br': 'luis.henrique',
    'jessyka.tavares@crasesigma.com.br': 'jessyka.tavares',
    'oscar.campelo@crasesigma.com.br': 'oscar.campelo',
    'jose.machado@crasesigma.com.br': 'jose.machado',
    'odilon@crasesigma.com.br': 'odilon',
    'nucleo@crasesigma.com.br': 'nucleo'
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
        print(f"Erro ao anexar o arquivo PDF: {e}")
        sys.stdout.flush()
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
            print(f"Erro ao anexar o arquivo TXT: {e}")
            sys.stdout.flush()
            return

    comando_sendemail = (
        f"sendEmail -o tls=no -f {remetente} -t {destinatario} -u \"{assunto}\" "
        f"-m \"{corpo_html}\" -s 172.16.0.4 -a \"{caminho_pdf}\""
    )
    
    if caminho_txt:
        comando_sendemail += f" -a \"{caminho_txt}\""

    resultado = os.system(comando_sendemail)
    
    if resultado != 0:
        logging.error(f"Falha ao enviar e-mail para {destinatario}")
        print(f"Falha ao enviar e-mail para {destinatario}")
        sys.stdout.flush()
    else:
        logging.info(f"E-mail enviado com sucesso para {destinatario}")
        print(f"E-mail enviado com sucesso para {destinatario}")
        sys.stdout.flush()


# Função para gerar PDF estilizado
def gerar_pdf_stilizado(dados, caminho_pdf, largura=landscape(A4)):
    logging.info(f"Gerando PDF {os.path.basename(caminho_pdf)}")
    print(f"Gerando PDF {os.path.basename(caminho_pdf)}")

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

# Updated function to process files matching "CONTAZZZ" pattern
def processar_arquivo_e_gerar_pdfs(diretorio_txt, largura=landscape(A4)):
    logging.info(f"Processando arquivos no diretório {diretorio_txt}")
    print(f"Processando arquivos no diretório {diretorio_txt}")
    sys.stdout.flush()

    remetente = "crase@crasemail.com.br"
    linhas_por_pessoa = {}

    # Filter files with "CONTAZZZ" in the name
    arquivos_txt = [f for f in os.listdir(diretorio_txt) if f.endswith('.txt') and "CONTAZZZ" in f]
    if len(arquivos_txt) == 0:
        logging.warning("Nenhum arquivo TXT com o padrão 'CONTAZZZ' encontrado.")
        print("Nenhum arquivo TXT com o padrão 'CONTAZZZ' encontrado.")
        sys.stdout.flush()
        return
    elif len(arquivos_txt) > 1:
        logging.warning("Mais de um arquivo TXT com o padrão 'CONTAZZZ' encontrado. Processando todos.")
        print("Mais de um arquivo TXT com o padrão 'CONTAZZZ' encontrado. Processando todos.")
        sys.stdout.flush()

    for arquivo in arquivos_txt:
        file_path = os.path.join(diretorio_txt, arquivo)
        logging.info(f"Arquivo TXT encontrado: {file_path}")
        print(f"Arquivo TXT encontrado: {file_path}")
        sys.stdout.flush()

        # Extract the date from the file name
        nome_arquivo = os.path.basename(file_path)
        data_auditagem = nome_arquivo.split('CONTAZZZ')[-1].split('.')[0]
        data_formatada = f"{data_auditagem[:2]}/{data_auditagem[2:4]}/{data_auditagem[4:]}"

        # Read the report file and group by consultant name
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

        # Generate PDFs and send by email
        for email, linhas in linhas_por_pessoa.items():
            dados = [cabecalho] + [linha[:-1] for linha in linhas]
            if len(dados) > 1:  # Only generate PDF if there is data
                caminho_pdf = f"/tmp/auditagem_{email.split('@')[0]}.pdf"

                gerar_pdf_stilizado(dados, caminho_pdf, largura)

                assunto = f"Auditagens das contas a pagar - {data_formatada} - {email.split('@')[0]}"
                enviar_email_com_anexo(remetente, assunto, caminho_pdf, email)
                time.sleep(5)

        # Generate the complete report
        dados_completo = [cabecalho] + [linha[:-1] for linhas in linhas_por_pessoa.values() for linha in linhas]
        caminho_pdf_completo = "/tmp/auditagem_completa.pdf"
        gerar_pdf_stilizado(dados_completo, caminho_pdf_completo, largura)

        assunto_completo = f"Auditagem Completa - Contas a Pagar - {data_formatada}"
        destinatarios_completos = [
            "carloscastroz@yahoo.com.br", 
            "mellod98@gmail.com"
        ]

        for destinatario in destinatarios_completos:
            enviar_email_com_anexo(remetente, assunto_completo, caminho_pdf_completo, destinatario)

        assunto_completo_txt = f"Auditagem Completa + TXT - Contas a Pagar - {data_formatada}"
        enviar_email_com_anexo(remetente, assunto_completo_txt, caminho_pdf_completo, "carla.castro@crasesigma.com.br", caminho_txt=file_path)

        # Move the TXT file to the backup directory
        caminho_backup = "/opt/backup/docctb/486ctxt/.backup"
        if not os.path.exists(caminho_backup):
            os.makedirs(caminho_backup)
        shutil.move(file_path, os.path.join(caminho_backup, os.path.basename(file_path)))
        print(f"Arquivo {file_path} movido para {caminho_backup}")

# Define directory and run the function
diretorio_txt = '/opt/backup/docctb/486ctxt/'

#sempre no ultimo do mês de manhã o programa do assueiro roda

processar_arquivo_e_gerar_pdfs(diretorio_txt, largura=landscape((700, 600)))
