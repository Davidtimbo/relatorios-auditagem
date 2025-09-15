# 📊 Auditagem de Relatórios

Este repositório contém scripts em **Python** para automatizar a **auditagem de relatórios de contas a pagar**, incluindo:

- Processamento de arquivos `.txt` com dados financeiros.
- Geração de relatórios em **PDF estilizado**.
- Distribuição automática dos relatórios por **e-mail** para cada consultor.
- Criação de relatório **consolidado** e envio para gestores.
- Movimentação automática dos arquivos para diretórios de **backup**.

---

## ⚙️ Funcionalidades principais

1. **Leitura de arquivos TXT** com padrão `CONTAZZZ*.txt`.
2. **Filtragem e agrupamento por consultor**, com base em mapeamento pré-definido.
3. **Geração de PDFs estilizados** com tabelas.
4. **Envio automático por e-mail**:
   - Relatório individual → enviado ao consultor correspondente.
   - Relatório completo → enviado para destinatários de auditoria.
   - Relatório completo + TXT → enviado a um responsável específico.
5. **Backup automático** dos arquivos processados.

---

## 📁 Estrutura de diretórios utilizada

- **Entrada de arquivos TXT:**  
  `/opt/backup/docctb/486ctxt/`

- **Backup dos arquivos TXT processados:**  
  `/opt/backup/docctb/486ctxt/.backup/`

- **Arquivos PDF temporários:**  
  `/tmp/`

- **Log de execução:**  
  `/home/****/auditagemRelatorio/auditagem.log`

---

## 🧩 Dependências

- **Python 3**
- **reportlab** (para gerar PDFs)
- **sendEmail** (para envio de e-mails via linha de comando)

Instale com:

```bash
pip install reportlab
```

No Linux, para instalar o sendEmail:

sudo apt-get install sendemail


🚀 Como executar

Ajuste os caminhos no script principal auditagemRelatorio.py, se necessário.

Certifique-se de que o diretório de entrada contém arquivos .txt no formato esperado (CONTAZZZ*.txt).

Execute:

```bash
python3 auditagemRelatorio.py
```

🔁 Execução automática (cron)

Para rodar automaticamente no último dia útil do mês pela manhã, configure no crontab (exemplo):

```bash
30   9   * *  *  root python3 /home/crase/AuditagemRelatorio/auditagemRelatorio.py  >/home/crase/AuditagemRelatorio/log_cron.txt 2>&1
```

---


## 📌 Observações importantes

- Os arquivos .txt devem seguir o padrão de formatação esperado (Consultor;Código;Local;...).

- Endereços de e-mail internos e IP do servidor SMTP foram substituídos por **** neste README para segurança.

- O uso de permissões ou envio de relatórios deve ser ajustado de acordo com a política interna da empresa.

## 📅 Exemplo

- Se existir um arquivo chamado:

- CONTAZZZ15092025.txt


- O sistema irá:

- Processar os dados do relatório referente a 15/09/2025.

- Gerar PDFs individuais para cada consultor.

- Enviar automaticamente por e-mail.

- Criar um PDF consolidado e distribuir aos gestores.
 ![WhatsApp Image 2025-09-15 at 10 54 08](https://github.com/user-attachments/assets/13e04c52-ddd5-42b1-b9ce-65725946489e)


- Mover o .txt original para o diretório de backup.
