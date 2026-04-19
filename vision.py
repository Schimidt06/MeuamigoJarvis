import io
import base64
import os
import pyautogui
from groq import Groq
from dotenv import load_dotenv
from logger import logger

load_dotenv()

_client = Groq(api_key=os.getenv("GROQ_API_KEY"))
_MODEL  = "meta-llama/llama-4-scout-17b-16e-instruct"


def analyze_screen(question: str = "O que está acontecendo nesta tela? Descreva em português de forma concisa.") -> str:
    logger.info("[VISION] Capturando tela...")
    shot = pyautogui.screenshot()

    buf = io.BytesIO()
    shot.save(buf, format="PNG")
    img_b64 = base64.b64encode(buf.getvalue()).decode()

    try:
        resp = _client.chat.completions.create(
            model=_MODEL,
            messages=[{
                "role": "user",
                "content": [
                    {"type": "image_url", "image_url": {"url": f"data:image/png;base64,{img_b64}"}},
                    {"type": "text",      "text": question},
                ],
            }],
            max_tokens=400,
        )
        result = resp.choices[0].message.content.strip()
        logger.info("[VISION] Análise concluída.")
        return result
    except Exception as e:
        logger.error("[VISION] Erro: {}", e)
        return "Não consegui analisar a tela neste momento, senhor."
