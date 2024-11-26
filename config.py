# config.py

# Binance API Bilgileri
API_KEY = "DgeBLXrlCHWGWQ4kOD8nNYfqhsSWFqJzWXpMpIiUXKpUxfmGhCJU4kcC0aRf04Ji"
API_SECRET = "ihXbNewTrSQcS4OC8NJJATDsXn7ksOKjKY5gaaF10ubtPars2URZGexiNuSjGCar"

# Telegram Bot Bilgileri
TELEGRAM_TOKEN = "8116604755:AAHZKJ9OEvJDwkpSxK2LOpZm8m8RXMES2Oo"
TELEGRAM_CHAT_ID = "546807193"

# Trading Parametreleri
INITIAL_BALANCE = 30  # USDT
MINIMUM_VOLUME = 1000000  # Minimum günlük işlem hacmi
MAX_COIN_PRICE = 1.0  # Maximum coin fiyatı
UPDATE_INTERVAL = 60  # Güncelleme aralığı (saniye)

# Neural Network Parametreleri
SEQUENCE_LENGTH = 60  # Tahmin için kullanılacak veri noktası sayısı
EPOCHS = 50
BATCH_SIZE = 32