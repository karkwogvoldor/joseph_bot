# 🎯 Joseph Bot — CS2 Utility Bot para Discord

Bot do Discord para busca de granadas (smokes, flashs, molotovs e HEs) do Counter-Strike 2, com vídeos e instruções de execução.

---

## 🚀 Tecnologias

- **Python 3.12**
- **Django 6.x** — ORM e Admin
- **discord.py** — Bot do Discord
- **PostgreSQL** — Banco de dados
- **BeautifulSoup4** — Scraper
- **python-dotenv** — Variáveis de ambiente

---

## ⚙️ Instalação

### 1. Clone o repositório

```bash
git clone https://github.com/seu-usuario/joseph_bot.git
cd joseph_bot
```

### 2. Crie e ative a venv

```bash
python -m venv .venv
.venv\Scripts\activate  # Windows
source .venv/bin/activate  # Linux/Mac
```

### 3. Instale as dependências

```bash
pip install -r requirements.txt
playwright install chromium
```

### 4. Configure o `.env`

Crie um arquivo `.env` na raiz do projeto:

```env
SECRET_KEY=sua_secret_key_aqui
DEBUG=True

DB_NAME=cs_nades_bot
DB_USER=postgres
DB_PASSWORD=sua_senha
DB_HOST=localhost
DB_PORT=5432

DISCORD_TOKEN=seu_token_do_discord
```

### 5. Rode as migrations

```bash
python manage.py migrate
```

### 6. Crie o superusuário (opcional)

```bash
python manage.py createsuperuser
```

### 7. Importe as granadas

```bash
python manage.py import_nades --mapa mirage
python manage.py import_nades --mapa inferno
python manage.py import_nades --mapa dust2
python manage.py import_nades --mapa ancient
python manage.py import_nades --mapa nuke
python manage.py import_nades --mapa anubis
python manage.py import_nades --mapa overpass
```

### 8. Inicie o bot

```bash
python manage.py runbot
```

---

## 🤖 Comandos do Bot

| Comando | Descrição |
|---|---|
| `!smoke <mapa> [destino]` | Busca smokes do mapa |
| `!flash <mapa> [destino]` | Busca flashbangs do mapa |
| `!molotov <mapa> [destino]` | Busca molotovs do mapa |
| `!he <mapa> [destino]` | Busca granadas HE do mapa |
| `!mapas` | Lista os mapas disponíveis |
| `!tipos` | Lista os tipos de granadas |
| `!ajuda <comando>` | Ajuda detalhada de um comando |
| `!help` | Lista todos os comandos |
| `@joseph_bot` | Mensagem de boas-vindas |

### Exemplos de uso

```
!smoke mirage          → lista todos os destinos de smoke no mirage
!smoke mirage janela   → lista as origens para smoke na janela
!flash inferno banana  → lista as origens para flash na banana
!molotov dust2         → lista todos os destinos de molotov no dust2
```

O bot suporta nomes em **português** e **inglês**:
```
!smoke mirage janela   ✅
!smoke mirage window   ✅
!smoke mirage janelao  ✅
```

---

## 🗺️ Mapas disponíveis

- Mirage
- Inferno
- Dust2
- Ancient
- Nuke
- Anubis
- Overpass

---

## 🗃️ Estrutura do projeto

```
joseph_bot/
├── bot/                        # App do bot Discord
│   ├── management/
│   │   └── commands/
│   │       └── runbot.py       # Comando para iniciar o bot
│   ├── bot.py                  # Lógica do bot
│   └── traducoes.py            # Dicionários de tradução PT-BR
├── core/                       # Configurações do Django
│   ├── settings.py
│   └── urls.py
├── nades/                      # App principal
│   ├── management/
│   │   └── commands/
│   │       └── import_nades.py # Scraper do csnades.app
│   ├── models.py               # Models Mapa e Granada
│   └── admin.py
├── .env                        # Variáveis de ambiente (não versionado)
├── manage.py
├── requirements.txt
└── Procfile
```

---

## 📦 Models

### Mapa
| Campo | Tipo | Descrição |
|---|---|---|
| nome | CharField | Nome do mapa |
| slug | SlugField | Identificador único |

### Granada
| Campo | Tipo | Descrição |
|---|---|---|
| mapa | ForeignKey | Mapa relacionado |
| tipo | CharField | smoke, flash, molotov, he |
| destino | CharField | Onde a granada cai |
| origem | CharField | De onde é jogada |
| lado | CharField | tt, ct ou ambos |
| video_url | URLField | Link do vídeo MP4 |
| thumbnail | URLField | Imagem de preview |
| posicao | CharField | Comando setpos para o CS2 |
| model_state | CharField | stand, crouch, etc |
| throw_type | CharField | left click, jumpthrow, etc |
| move_keys | CharField | Teclas usadas |
| air_time | CharField | Tempo no ar |
| descricao | TextField | Dica de execução |
| origem_url | URLField | URL original no csnades.app |

---

## 🔧 Admin

Acesse `http://localhost:8000/admin` para gerenciar granadas e mapas manualmente.

---

## 📝 Licença

Projeto desenvolvido para fins educacionais. Os vídeos são de propriedade do [csnades.app](https://csnades.app).
