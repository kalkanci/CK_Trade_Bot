# config.py

# Binance API Bilgileri
API_KEY = "."
API_SECRET = "."

# Telegram Bot Bilgileri
TELEGRAM_TOKEN = "."
TELEGRAM_CHAT_ID = "."

# Trading Parametreleri
INITIAL_BALANCE = 30  # USDT
MINIMUM_VOLUME = 1000000  # Minimum günlük işlem hacmi
MAX_COIN_PRICE = 1.0  # Maximum coin fiyatı
UPDATE_INTERVAL = 60  # Güncelleme aralığı (saniye)

# Neural Network Parametreleri
SEQUENCE_LENGTH = 60  # Tahmin için kullanılacak veri noktası sayısı
EPOCHS = 50
BATCH_SIZE = 32
