# Moleculens - Conversor de Imagem de Molécula

Uma ferramenta web simples e poderosa para **digitalizar estruturas químicas a partir de imagens**.  
A aplicação utiliza **Python**, **Flask**, **Docker** e **RDKit** para extrair, analisar e exibir dados moleculares de forma interativa.

![Demonstração do Moleculens](https://i.imgur.com/nf982qB.gif)
---

##  Funcionalidades

- **Conversão Inteligente:** Usa o OSRA via Docker para converter imagens de moléculas em SMILES.  
- **Múltiplos Métodos de Upload:** Upload por clique, arrastar e soltar, colar da área de transferência (Ctrl+V) ou capturar foto no celular.  
- **Análise Química Completa:** Exibe SMILES, InChI e InChIKey.  
- **Cálculo de Propriedades:** Peso Molecular, Fórmula, LogP, TPSA, etc.  
- **Visualização 2D e 3D:**
  - Desenho 2D em SVG com fundo transparente e opção de download.
  - Visualizador 3D interativo com múltiplos estilos (linhas, varetas, bolas e varetas, esferas) e ajuste de cor de fundo.
- **Integração com PubChem:** InChIKey com link direto para busca.  
- **Interface Moderna e Responsiva:**
  - Design adaptável a desktop, tablet e celular.
  - **Modo Escuro** com preferência salva no navegador.
  - Processamento em tempo real com opção de cancelamento.

---

## ⚙️ Como Funciona

A aplicação combina várias tecnologias:

- **Frontend:** HTML, CSS e JavaScript.
- **Backend:** Python + Flask.
- **Inteligência Química:** RDKit para validação, cálculo e renderização molecular.
- **Reconhecimento de Imagem:** OSRA dentro de um contêiner Docker, garantindo isolamento e segurança.

---

##  Guia de Instalação

### 1) Clonar o Repositório

```bash
git clone https://github.com/seu-usuario/nome-do-seu-repositorio.git
cd nome-do-seu-repositorio
```

> Substitua a URL pelo seu próprio repositório.

---

### 2) Instalar Dependências (Docker e Miniconda)

#### Windows 10/11

**Instalar WSL2 (se necessário)**
```powershell
wsl --install
```

- Baixe e instale o Docker Desktop para Windows. Durante a instalação, habilite "Use WSL 2".  
- Após a instalação, abra o Docker Desktop e aguarde até mostrar "Running".
- Baixe e instale o Miniconda (instalador para Windows 64-bit).  
- Use o terminal "Anaconda Prompt (Miniconda3)" para os próximos passos.

#### Linux (Ubuntu / Debian)

**Instalar Docker**
```bash
sudo apt update
sudo apt install -y apt-transport-https ca-certificates curl software-properties-common
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /usr/share/keyrings/docker-archive-keyring.gpg
echo "deb [arch=amd64 signed-by=/usr/share/keyrings/docker-archive-keyring.gpg] https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io
sudo usermod -aG docker ${USER}
```
Feche e reabra o terminal para aplicar as permissões.

**Instalar Miniconda**
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```
Siga as instruções, aceite a licença e no final escolha inicializar o Miniconda. Reabra o terminal.

#### Linux (Manjaro / Arch)

**Instalar Docker**
```bash
sudo pacman -Syu docker
sudo systemctl start docker.service
sudo systemctl enable docker.service
sudo usermod -aG docker ${USER}
```
Reinicie ou reabra o terminal.

**Instalar Miniconda** (mesmo procedimento do Ubuntu/Debian):
```bash
wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh
bash Miniconda3-latest-Linux-x86_64.sh
```

---

### 3) Preparar o Ambiente do Projeto (Conda)

```bash
conda create -n molconverter python=3.11
conda activate molconverter
conda install -c conda-forge rdkit flask waitress
```

---

### 4) Baixar a Imagem do OSRA (Docker)

```bash
docker pull daverona/osra
```

---

## ▶️ Executando a Aplicação

Antes de iniciar, verifique:
- Docker Desktop (ou serviço Docker no Linux) está ativo.
- Ambiente Conda está ativado:
```bash
conda activate molconverter
```
- Você está na pasta do projeto.

Execute:
```bash
python app.py
```

Abra no navegador:
```
http://127.0.0.1:8080
```

---

## 🛠 Solução de Problemas (Troubleshooting)

- **Comando `docker` não encontrado:** Verifique instalação do Docker e se o serviço está rodando.
- **Comando `conda` não encontrado:** Confirme instalação do Miniconda e reinicie o terminal.
- **Conversão falha:** Verifique se o Docker está ativo e se a imagem `daverona/osra` foi baixada corretamente.

---

## 📜 Licença

Este projeto é distribuído sob a licença MIT — consulte o arquivo `LICENSE` para mais detalhes.
```

Se quiser, eu já salvo esse texto em um arquivo `README.md` aqui e te forneço um link para download — quer que eu faça isso?