# 🦾 O Meu Amigo J.A.R.V.I.S

Um assistente de inteligência artificial construído 100% em Python, operando no modelo State-Machine. Ele responde ativamente à sua voz, aciona scripts de automação, relatórios de sistema, e realiza Web Scraping inteligente enquanto usa uma voz hiper-realista da ElevenLabs.

---

## 🚀 Funcionalidades da Máquina

O J.A.R.V.I.S possui uma inteligência baseada em Dois Estágios (Passivo-Ativo) garantindo foco total no que ele está escutando, sem gastar processamento à toa.

### Como Acordá-lo (Estágio Passivo)
- O Jarvis só ouve se você chamar pelo seu nome (Módulo Wake Word).
- Diga apenas **"Jarvis"**. 
- Ele ativará instantaneamente um áudio local randômico dizendo _"Pois não, senhor?"_ e ligará o alerta visual verde.
- Você tem 10 segundos exatos para ditar uma das ordens abaixo.

### Comandos Críticos (Estágio Ativo)
* **🗣️ "Jarvis Apresentação"**: Fuso-horário dinâmico que gera "Bom Dia / Boa Tarde / Boa Noite", força uma aba Chrome em modo Kiosk App exclusivo, toca música na batida perfeita e carrega scripts na tela.
* **🗣️ "Notícias"**: Realiza uma varredura silenciosa nas sessões ocultas da Web (UOL), faz scraping das Tags HTML de títulos de Política e Mercado Financeiro, e dita elas com Voz Sintética da ElevenLabs.
* **🗣️ "Previsão do tempo"**: Utiliza seu endereço IP Global para injetar Latitude e Longitude num radar meteorológico real (Open-Meteo) e fala a temperatura exata.
* **🗣️ "Status do Sistema"**: Através da injeção no Kernel via `psutil`, checa a memória RAM, bateria restante e processador do Windows nativamente.
* **🗣️ "Hora do trabalho", "Trancar Sistema", "Pesquisar sobre {X}"...** e ferramentas padrão. 

---

## 🛠️ Tecnologias Envolvidas
- **Processamento de Áudio Local:** `vosk` & `sounddevice`
- **Voz Cinematográfica e IA Lexical:** API V2 Multi-Lingual da `ElevenLabs`
- **Edição e Mixagem ao Vivo:** `pydub` e `winsound`
- **Hacking de Software e Rotas OS:** `subprocess`, `ctypes`, `os`
- **Web Scraping:** `beautifulsoup4` e `requests`

> ✨ **Arquitetura Zero-Latency Cache:** O Jarvis queima chamadas limitadas da nuvem apenas na primeira inicialização. Títulos padrões como Bom Dia, Mensagem de Aguardar, e Saudações Curtas ficam instaladas localmente em cache invisível de `.mp3`.

---

## 💻 Como Instalar e Configurar o Núcleo

1. **Clone do Repositório**
   ```bash
   git clone https://github.com/Schimidt06/MeuamigoJarvis.git
   cd MeuamigoJarvis
   ```

2. **Instale as Bibliotecas Exigidas**
   ```bash
   pip install -r requirements.txt
   ```
   *(Atenção Especial ao módulo Vosk, que contém o modelo offline de fala treinado localmente).*

3. **Crie suas Chaves de Ignição (.env)**
   Para o Jarvis não te custar a cabeça (nem ser rackeado), o Token da API foi escondido. 
   **Crie um arquivo chamado `.env` no fundo da sua pasta principal.** Nele coloque:
   ```env
   ELEVENLABS_API_KEY=sk_coloquesuachaveaqui12345
   ```
   *Se não possuir a chave, crie na biblioteca de vozes [ElevenLabs](elevenlabs.io).*

4. **Rodando a Matriz!**
   Abra o Terminal.
   ```bash
   python jarvis.py
   ```
   *Se quiser esconde-lo de vez após testar, renomeie para `.pyw` e coloque num atalho da pasta `shell:startup` para subir com o Windows sem interfaces pretas.*
