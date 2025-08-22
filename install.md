Guia de Instalação do Docker e Docker Compose
1. Instalar o Docker
Ubuntu/Debian
# Atualizar pacotes
sudo apt-get update

# Instalar pacotes necessários
sudo apt-get install -y ca-certificates curl gnupg lsb-release

# Adicionar chave GPG oficial
sudo mkdir -m 0755 -p /etc/apt/keyrings
curl -fsSL https://download.docker.com/linux/ubuntu/gpg | sudo gpg --dearmor -o /etc/apt/keyrings/docker.gpg

# Adicionar repositório Docker
echo \
  "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] \
  https://download.docker.com/linux/ubuntu $(lsb_release -cs) stable" \
  | sudo tee /etc/apt/sources.list.d/docker.list > /dev/null

# Instalar Docker
sudo apt-get update
sudo apt-get install -y docker-ce docker-ce-cli containerd.io

Verificar instalação
docker --version

2. Instalar o Docker Compose
# Baixar última versão
sudo curl -L "https://github.com/docker/compose/releases/latest/download/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose

# Dar permissão de execução
sudo chmod +x /usr/local/bin/docker-compose

# Verificar instalação
docker-compose --version

3. Rodar um projeto com Docker Compose

Crie um arquivo docker-compose.yml no seu projeto.
Exemplo:

version: "3.9"
services:
  app:
    image: nginx:latest
    ports:
      - "8080:80"


Suba os containers:

docker-compose up -d


Verifique os containers rodando:

docker ps


Para parar os containers:

docker-compose down
