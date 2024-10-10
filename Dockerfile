# Użyj oficjalnego obrazu Pythona jako bazy
FROM python:3.8-slim

# Ustaw katalog roboczy
WORKDIR /app

# Skopiuj plik requirements.txt do katalogu roboczego
COPY requirements.txt .

# Zainstaluj wymagane pakiety
RUN pip install --no-cache-dir -r requirements.txt

# Skopiuj kod aplikacji do katalogu roboczego
COPY . .

# Określ, jakie polecenie ma być uruchamiane przy starcie kontenera
CMD ["flask", "run", "--host=0.0.0.0"]
