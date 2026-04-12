# 🦾 O Meu Amigo P.I.T.O.C.O

Um assistente de inteligência artificial construído 100% em Python, operando no modelo State-Machine com o protocolo **Stark Industries Vision Hub**. Ele responde ativamente à sua voz, aciona scripts de automação, relatórios de sistema, e possui uma interface neural responsiva.

---

## 🚀 Funcionalidades da Máquina

O P.I.T.O.C.O possui uma inteligência baseada em Dois Estágios (Passivo-Ativo) garantindo foco total no que ele está escutando.

### Como Acordá-lo (Estágio Passivo)
- O Pitoco só ouve se você chamar pelo seu nome (Módulo Wake Word).
- Diga apenas **"Pitoco"**. 
- Ele ativará instantaneamente respondendo com o tom assertivo do Tony Stark e ligará o alerta visual.
- Você tem 10 segundos exatos para ditar uma das ordens abaixo.

### Comandos Críticos (Estágio Ativo)
* **🗣️ "Pitoco Cheguei"**: Inicia o **Vision Hub**, fuso-horário dinâmico, força uma aba Chrome em modo Kiosk App exclusivo, toca música (AC/DC) e abre o Hub Neural.
* **🗣️ "Notícias"**: Realiza uma varredura silenciosa nas sessões ocultas da Web (UOL), faz scraping e dita os títulos.
* **🗣️ "Previsão do tempo"**: Utiliza radar meteorológico real (Open-Meteo) e fala a temperatura exata.
* **🗣️ "Status do Sistema"**: Checa a memória RAM, bateria restante e processador do Windows nativamente.

---

## 🛠️ Tecnologias Envolvidas
- **Processamento de Áudio Local:** `vosk` & `sounddevice`
- **Inteligência de Comando:** `rapidfuzz` (Fuzzy Matching)
- **Voz Cinematográfica:** API V2 Multi-Lingual da `ElevenLabs`
- **Interface Visual:** `Flask` + `HTML5 Canvas` (Rede Neural Responsiva)
- **Web Scraping:** `beautifulsoup4` e `requests`

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

3. **Crie suas Chaves de Ignição (.env)**
   Crie um arquivo `.env` e coloque:
   ```env
   ELEVENLABS_API_KEY=sua_chave_aqui
   ```

4. **Rodando a Matriz!**
   ```bash
   python jarvis.py
   ```
