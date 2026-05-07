# 🤖 Edge Bot Pro

Bot de predicciones deportivas con IA y análisis de valor (+EV)

## 📋 Requisitos

- Python 3.9+
- Cuentas necesarias:
  - [Telegram Bot](https://core.telegram.org/bots)
  - [Groq API](https://groq.com)
  - [The Odds API](https://the-odds-api.com)

## 🚀 Instalación

```bash
# 1. Clonar repositorio
git clone https://github.com/jrojo0153-ux/Edge-Bot-Pro
cd Edge-Bot-Pro

# 2. Instalar dependencias
pip install -r requirements.txt

# 3. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales reales

# 4. Crear carpetas necesarias
mkdir -p core data ml logs

# 5. Ejecutar
python bot.py           # Modo ESPN + Groq IA
# O
python pipeline.py      # Modo Odds API + ML
# O
python scheduler.py     # Modo automático programado
