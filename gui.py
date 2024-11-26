# gui.py

from PyQt6.QtWidgets import *
from PyQt6.QtCore import *
from PyQt6.QtGui import *
from PyQt6.QtCharts import *
import sys
import threading

from bot import CryptoTradingBot
from config import *

class TradingBotGUI(QMainWindow):
    def closeEvent(self, event):
        """Program kapatıldığında"""
        self.bot.save_current_state()  # Durumu kaydet
        self.bot.stop()
        event.accept()


    def __init__(self):
        super().__init__()
        self.bot = CryptoTradingBot()
        self.bot.on_trade_callback = self.handle_trade
        self.bot.on_error_callback = self.handle_error
        
        self.init_ui()
        self.update_signal.connect(self.update_ui)
        self.error_signal.connect(self.show_error)

    def init_ui(self):
        """Ana arayüzü oluştur"""
        self.setWindowTitle('Crypto Trading Bot')
        self.setGeometry(100, 100, 1200, 800)

        # Ana widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)

        # Üst panel
        top_panel = QHBoxLayout()
        
        # Coin seçimi
        self.coin_combo = QComboBox()
        self.update_coin_list()
        self.coin_combo.currentTextChanged.connect(self.on_coin_selected)
        top_panel.addWidget(QLabel('Select Coin:'))
        top_panel.addWidget(self.coin_combo)

        # Start/Stop butonu
        self.toggle_button = QPushButton('Start Bot')
        self.toggle_button.clicked.connect(self.toggle_bot)
        top_panel.addWidget(self.toggle_button)

        layout.addLayout(top_panel)

        # Grafik
        self.chart_view = QChartView()
        self.chart_view.setMinimumHeight(400)
        layout.addWidget(self.chart_view)

        # Alt panel
        bottom_panel = QHBoxLayout()

        # Performance metrics
        metrics_group = QGroupBox('Performance Metrics')
        metrics_layout = QVBoxLayout()
        
        self.balance_label = QLabel('Balance: 0 USDT')
        self.profit_label = QLabel('Total Profit: 0 USDT')
        self.trades_label = QLabel('Total Trades: 0')
        self.win_rate_label = QLabel('Win Rate: 0%')
        
        metrics_layout.addWidget(self.balance_label)
        metrics_layout.addWidget(self.profit_label)
        metrics_layout.addWidget(self.trades_label)
        metrics_layout.addWidget(self.win_rate_label)
        
        metrics_group.setLayout(metrics_layout)
        bottom_panel.addWidget(metrics_group)

        # İşlem geçmişi
        history_group = QGroupBox('Trade History')
        history_layout = QVBoxLayout()
        
        self.history_table = QTableWidget()
        self.history_table.setColumnCount(5)
        self.history_table.setHorizontalHeaderLabels([
            'Time', 'Symbol', 'Side', 'Quantity', 'Price'
        ])
        
        history_layout.addWidget(self.history_table)
        history_group.setLayout(history_layout)
        bottom_panel.addWidget(history_group)

        layout.addLayout(bottom_panel)

        # Timer
        self.update_timer = QTimer()
        self.update_timer.timeout.connect(self.update_data)
        self.update_timer.start(5000)

    def update_chart(self, df):
        """Grafikleri güncelle"""
        chart = QChart()
        
        # Fiyat serisi
        price_series = QLineSeries()
        price_series.setName("Price")
        
        # RSI serisi
        rsi_series = QLineSeries()
        rsi_series.setName("RSI")
        
        # MACD serisi
        macd_series = QLineSeries()
        macd_series.setName("MACD")
        
        # Verileri ekle
        for index, row in df.iterrows():
            ms = int(index.timestamp() * 1000)
            price_series.append(ms, row['close'])
            rsi_series.append(ms, row['RSI'])
            macd_series.append(ms, row['MACD'])
        
        chart.addSeries(price_series)
        chart.addSeries(rsi_series)
        chart.addSeries(macd_series)
        
        # Eksenleri ayarla
        axis_x = QDateTimeAxis()
        axis_x.setFormat("HH:mm:ss")
        chart.addAxis(axis_x, Qt.AlignmentFlag.AlignBottom)
        
        axis_y = QValueAxis()
        chart.addAxis(axis_y, Qt.AlignmentFlag.AlignLeft)
        
        price_series.attachAxis(axis_x)
        price_series.attachAxis(axis_y)
        rsi_series.attachAxis(axis_x)
        rsi_series.attachAxis(axis_y)
        macd_series.attachAxis(axis_x)
        macd_series.attachAxis(axis_y)
        
        self.chart_view.setChart(chart)


    def update_coin_list(self):
        """Coin listesini güncelle"""
        self.coin_combo.clear()
        viable_coins = self.bot.get_viable_coins()
        for coin in viable_coins:
            self.coin_combo.addItem(coin['symbol'])

    def toggle_bot(self):
        """Bot'u başlat/durdur"""
        if self.bot.is_running:
            self.bot.stop()
            self.toggle_button.setText('Start Bot')
        else:
            self.bot.start()
            self.toggle_button.setText('Stop Bot')

    def update_history_table(self):
        """İşlem geçmişini güncelle"""
        self.history_table.setRowCount(len(self.bot.trading_history))
        
        for i, trade in enumerate(self.bot.trading_history):
            self.history_table.setItem(i, 0, QTableWidgetItem(str(trade['timestamp'])))
            self.history_table.setItem(i, 1, QTableWidgetItem(trade['symbol']))
            self.history_table.setItem(i, 2, QTableWidgetItem(trade['side']))
            self.history_table.setItem(i, 3, QTableWidgetItem(str(trade['quantity'])))
            self.history_table.setItem(i, 4, QTableWidgetItem(str(trade['price'])))

    def update_metrics(self):
        """Performans metriklerini güncelle"""
        metrics = self.bot.get_performance_metrics()
        
        self.balance_label.setText(f"Balance: {metrics['current_balance']:.2f} USDT")
        self.profit_label.setText(f"Total Profit: {metrics['total_profit']:.2f} USDT")
        self.trades_label.setText(f"Total Trades: {metrics['total_trades']}")
        self.win_rate_label.setText(f"Win Rate: {metrics['win_rate']:.1f}%")

    def update_data(self):
        """Tüm verileri güncelle"""
        if self.bot.current_coin:
            df = self.bot.get_historical_data(self.bot.current_coin)
            if df is not None:
                self.update_chart(df)
        
        self.update_metrics()
        self.update_history_table()

    def handle_trade(self, trade_info):
        """Yeni işlem gerçekleştiğinde"""
        self.update_signal.emit(trade_info)

    def handle_error(self, error_message):
        """Hata durumunda"""
        self.error_signal.emit(error_message)

    def show_error(self, message):
        """Hata mesajını göster"""
        QMessageBox.critical(self, 'Error', message)

    def on_coin_selected(self, symbol):
        """Coin seçildiğinde"""
        self.bot.current_coin = symbol
        self.update_data()

    def closeEvent(self, event):
        """Program kapatıldığında"""
        self.bot.stop()
        event.accept()

    def update_ui(self, trade_info):
        """UI güncellemelerini yap"""
        self.update_data()
        QMessageBox.information(
            self,
            'Trade Executed',
            f"New trade executed:\n{trade_info['side']} {trade_info['quantity']} {trade_info['symbol']} at {trade_info['price']}"
        )