# AllSocialMidia - Produtora Automatizada de Vídeos 🎬

Este projeto é uma ferramenta automatizada para criação e publicação em massa de vídeos curtos (Shorts, Reels, TikTok, Kwai) e longos. Ele utiliza Inteligência Artificial para roteirizar, narrar e editar vídeos automaticamente, além de possuir robôs (bots) para publicá-los nas redes sociais.

## 🚀 Principais Recursos

- **Geração de Roteiros Virais:** Utiliza a API do Google Gemini para criar roteiros otimizados.
- **Vozes Neurais:** Narrações realistas geradas através do Edge-TTS.
- **B-Roll Inteligente:** Busca automaticamente vídeos de fundo na API do Pexels baseados no contexto.
- **Edição e Efeitos:** Legendas no estilo "Hormozi" com cores de destaque e ajuste automático de áudio (ducking) com trilhas sonoras de fundo.
- **Publicação Automática (Bots):** Scripts em Node.js (Puppeteer) e Python para postar automaticamente no Instagram, YouTube e Kwai.

## ⚙️ Pré-requisitos e Configuração

Para que o sistema funcione corretamente, você precisa configurar um arquivo `.env` na raiz do projeto (use o `.env.example` como base) contendo suas chaves de API:

```env
GEMINI_API_KEY=sua_chave_do_google_gemini
PEXELS_API_KEY=sua_chave_do_pexels
```

## 🛠️ Como Usar (Geração de Vídeos)

Você pode iniciar a interface principal do sistema de três formas:

1. **Modo Interativo (CLI):**
   Abre um menu no terminal onde você pode escolher o nicho, tópico, formato (9:16, 16:9, 1:1), música de fundo e cor das legendas.
   ```bash
   python main.py
   ```

2. **Modo Web (Interface Gráfica):**
   Inicia um servidor local com uma interface web para gerenciar a criação dos vídeos.
   ```bash
   python main.py --web
   ```

3. **Geração em Lote (Scripts prontos):**
   Para gerar dezenas de vídeos de uma vez sobre um nicho específico (como a filosofia estóica), basta rodar os scripts pré-configurados:
   ```bash
   python generate_kwai.py
   # ou
   python generate_kwai_remaining.py
   ```
   Os vídeos finalizados e os arquivos associados serão salvos na pasta `output/`.

## 🤖 Como Usar (Publicação Automática)

O projeto possui comandos mapeados no `package.json` para facilitar a execução dos bots de publicação. Você pode usar os seguintes comandos via NPM:

**Instagram:**
- `npm run bot:instagram` - Publicar posts.
- `npm run generate:instagram:reels` - Gera pacote para Reels.
- *(Também há comandos para follow/delete em massa: `npm run bot:instagram:follow`)*

**YouTube:**
- `npm run bot:youtube:shorts` - Publica YouTube Shorts.
- `npm run bot:youtube:longs` - Publica vídeos longos.
- `npm run bot:youtube:community` - Publica posts na comunidade.

**Kwai:**
- `npm run bot:kwai:shorts` - Publica no Kwai.
- `npm run generate:kwai:shorts` - Gera pacote de vídeos para Kwai.

## 📁 Estrutura de Pastas

- `/src/` - Núcleo da aplicação em Python (geração de conteúdo, áudio, vídeo, download de mídias).
- `/bots/` - Scripts de automação (Puppeteer/Node.js e Python) para interagir com as plataformas.
- `/assets/` - Recursos estáticos (fontes, trilhas sonoras).
- `/output/` - Onde os vídeos e kits finais gerados são armazenados.
- `/data/` e `/chrome_profile/` - Dados locais e sessão do navegador para os bots (mantém os logins salvos).

---

> **Dica:** Sempre garanta que o ambiente virtual (`.venv`) está ativo antes de rodar os scripts Python. Use `source .venv/bin/activate` (Linux/Mac) ou `.venv\Scripts\activate` (Windows).
