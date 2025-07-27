"""
Market Mirror - Data Ingestion Module
Handles data collection from various market APIs with caching and rate limiting.
"""

import json
import time
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Union
import urllib.request
import urllib.parse

class DataIngestionError(Exception):
    """Custom exception for data ingestion errors"""
    pass

class MarketDataIngestion:
    """
    Unified data ingestion class supporting multiple market types:
    - Stocks (Yahoo Finance simulation)
    - Cryptocurrencies (CoinGecko simulation)  
    - E-commerce (Mock data)
    """
    
    def __init__(self):
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache
        self.rate_limit_delay = 1  # 1 second between requests
        self.last_request_time = 0
        
    def _rate_limit(self):
        """Implement rate limiting between API calls"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.rate_limit_delay:
            time.sleep(self.rate_limit_delay - elapsed)
        self.last_request_time = time.time()
    
    def _get_cache_key(self, market_type: str, symbols: List[str], duration: str) -> str:
        """Generate cache key for request"""
        symbols_str = ','.join(sorted(symbols))
        return f"{market_type}:{symbols_str}:{duration}"
    
    def _is_cache_valid(self, cache_key: str) -> bool:
        """Check if cached data is still valid"""
        if cache_key not in self.cache:
            return False
        
        cache_time = self.cache[cache_key]['timestamp']
        return (time.time() - cache_time) < self.cache_ttl
    
    def _generate_mock_stock_data(self, symbol: str, duration: str) -> Dict:
        """Generate mock stock data for demonstration"""
        base_prices = {
            'AAPL': 190.50,
            'GOOGL': 140.30,
            'MSFT': 350.75,
            'TSLA': 245.80,
            'AMZN': 180.25
        }
        
        base_price = base_prices.get(symbol, 100.0)
        
        # Generate historical data points
        days = {'1d': 1, '7d': 7, '1m': 30, '3m': 90}.get(duration, 7)
        history = []
        
        current_price = base_price
        for i in range(days, -1, -1):
            date = datetime.now() - timedelta(days=i)
            # Simulate price movement with random walk
            change_pct = (hash(f"{symbol}{date.date()}") % 1000) / 10000 - 0.05  # -5% to +5%
            current_price *= (1 + change_pct)
            
            history.append({
                'date': date.strftime('%Y-%m-%d'),
                'open': current_price * 0.999,
                'high': current_price * 1.02,
                'low': current_price * 0.98,
                'close': current_price,
                'volume': abs(hash(f"{symbol}{date}") % 10000000) + 1000000
            })
        
        latest = history[-1]
        previous = history[-2] if len(history) > 1 else history[-1]
        
        return {
            'symbol': symbol,
            'name': f"{symbol} Inc.",
            'current_price': latest['close'],
            'price_change': latest['close'] - previous['close'],
            'price_change_percentage': ((latest['close'] - previous['close']) / previous['close']) * 100,
            'market_cap': latest['close'] * 1000000000,  # Mock market cap
            'volume': latest['volume'],
            'high_24h': max(h['high'] for h in history[-2:]),
            'low_24h': min(h['low'] for h in history[-2:]),
            'history': history,
            'last_updated': datetime.now().isoformat()
        }
    
    def _generate_mock_crypto_data(self, symbol: str, duration: str) -> Dict:
        """Generate mock cryptocurrency data for demonstration"""
        base_prices = {
            'BTC': 65000.0,
            'ETH': 3200.0,
            'SOL': 180.0,
            'ADA': 0.45,
            'DOT': 7.50
        }
        
        base_price = base_prices.get(symbol, 1.0)
        
        # Generate historical data points
        days = {'1d': 1, '7d': 7, '1m': 30, '3m': 90}.get(duration, 7)
        history = []
        
        current_price = base_price
        for i in range(days, -1, -1):
            date = datetime.now() - timedelta(days=i)
            # Crypto tends to be more volatile
            change_pct = (hash(f"{symbol}{date.date()}") % 2000) / 10000 - 0.1  # -10% to +10%
            current_price *= (1 + change_pct)
            
            history.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': current_price,
                'volume': abs(hash(f"{symbol}{date}") % 1000000000) + 10000000
            })
        
        latest = history[-1]
        previous = history[-2] if len(history) > 1 else history[-1]
        
        return {
            'symbol': symbol,
            'name': f"{symbol} Token",
            'current_price': latest['price'],
            'price_change': latest['price'] - previous['price'],
            'price_change_percentage': ((latest['price'] - previous['price']) / previous['price']) * 100,
            'market_cap': latest['price'] * 21000000,  # Mock circulating supply
            'volume': latest['volume'],
            'high_24h': max(h['price'] for h in history[-2:]) * 1.05,
            'low_24h': min(h['price'] for h in history[-2:]) * 0.95,
            'history': history,
            'last_updated': datetime.now().isoformat()
        }
    
    def _generate_mock_ecommerce_data(self, product_id: str, duration: str) -> Dict:
        """Generate mock e-commerce product data for demonstration"""
        base_products = {
            'iPhone15': {'name': 'iPhone 15 Pro', 'base_price': 999.0, 'category': 'Electronics'},
            'AirPods': {'name': 'AirPods Pro', 'base_price': 249.0, 'category': 'Audio'},
            'MacBook': {'name': 'MacBook Air M2', 'base_price': 1199.0, 'category': 'Computers'},
            'iPad': {'name': 'iPad Pro', 'base_price': 799.0, 'category': 'Tablets'},
            'Watch': {'name': 'Apple Watch Ultra', 'base_price': 799.0, 'category': 'Wearables'}
        }
        
        product = base_products.get(product_id, {'name': f'Product {product_id}', 'base_price': 99.0, 'category': 'General'})
        base_price = product['base_price']
        
        # Generate pricing history
        days = {'1d': 1, '7d': 7, '1m': 30, '3m': 90}.get(duration, 7)
        history = []
        
        current_price = base_price
        for i in range(days, -1, -1):
            date = datetime.now() - timedelta(days=i)
            # E-commerce prices are more stable but can have promotions
            change_pct = (hash(f"{product_id}{date.date()}") % 200) / 10000 - 0.01  # -1% to +1%
            # Occasionally simulate bigger discounts (sales events)
            if hash(f"sale{product_id}{date.date()}") % 100 < 5:  # 5% chance of sale
                change_pct = -0.15  # 15% discount
            
            current_price = max(current_price * (1 + change_pct), base_price * 0.7)  # Min 30% off
            
            history.append({
                'date': date.strftime('%Y-%m-%d'),
                'price': current_price,
                'sales_volume': abs(hash(f"{product_id}{date}") % 1000) + 50,
                'availability': 'In Stock' if hash(f"stock{product_id}{date}") % 10 > 1 else 'Limited Stock'
            })
        
        latest = history[-1]
        previous = history[-2] if len(history) > 1 else history[-1]
        
        return {
            'product_id': product_id,
            'name': product['name'],
            'category': product['category'],
            'current_price': latest['price'],
            'price_change': latest['price'] - previous['price'],
            'price_change_percentage': ((latest['price'] - previous['price']) / previous['price']) * 100,
            'sales_volume': latest['sales_volume'],
            'availability': latest['availability'],
            'average_rating': 4.0 + (hash(f"rating{product_id}") % 10) / 10,  # 4.0-4.9 rating
            'review_count': abs(hash(f"reviews{product_id}") % 10000) + 100,
            'history': history,
            'last_updated': datetime.now().isoformat()
        }
    
    def fetch_market_data(self, market_type: str, symbols: List[str], duration: str) -> List[Dict]:
        """
        Fetch market data for specified symbols and duration
        
        Args:
            market_type: 'stocks', 'crypto', or 'ecommerce'
            symbols: List of symbols/product IDs to fetch
            duration: Time duration ('1d', '7d', '1m', '3m')
            
        Returns:
            List of market data dictionaries
        """
        cache_key = self._get_cache_key(market_type, symbols, duration)
        
        # Check cache first
        if self._is_cache_valid(cache_key):
            print(f"Returning cached data for {cache_key}")
            return self.cache[cache_key]['data']
        
        print(f"Fetching fresh data for {market_type}: {symbols} ({duration})")
        
        # Apply rate limiting
        self._rate_limit()
        
        try:
            results = []
            
            for symbol in symbols:
                if market_type == 'stocks':
                    data = self._generate_mock_stock_data(symbol, duration)
                elif market_type == 'crypto':
                    data = self._generate_mock_crypto_data(symbol, duration)
                elif market_type == 'ecommerce':
                    data = self._generate_mock_ecommerce_data(symbol, duration)
                else:
                    raise DataIngestionError(f"Unsupported market type: {market_type}")
                
                results.append(data)
            
            # Cache the results
            self.cache[cache_key] = {
                'data': results,
                'timestamp': time.time()
            }
            
            return results
            
        except Exception as e:
            raise DataIngestionError(f"Failed to fetch market data: {str(e)}")
    
    def get_supported_symbols(self, market_type: str) -> List[str]:
        """Get list of supported symbols for a market type"""
        if market_type == 'stocks':
            return ['AAPL', 'GOOGL', 'MSFT', 'TSLA', 'AMZN', 'NVDA', 'META', 'NFLX']
        elif market_type == 'crypto':
            return ['BTC', 'ETH', 'SOL', 'ADA', 'DOT', 'LINK', 'UNI', 'AVAX']
        elif market_type == 'ecommerce':
            return ['iPhone15', 'AirPods', 'MacBook', 'iPad', 'Watch', 'PS5', 'Switch', 'XBox']
        else:
            return []
    
    def clear_cache(self):
        """Clear all cached data"""
        self.cache.clear()
        print("Cache cleared")

# Example usage and testing
if __name__ == "__main__":
    # Initialize the data ingestion system
    ingestion = MarketDataIngestion()
    
    # Test crypto data fetching
    print("=== Testing Crypto Data Ingestion ===")
    crypto_data = ingestion.fetch_market_data('crypto', ['BTC', 'ETH', 'SOL'], '7d')
    for data in crypto_data:
        print(f"{data['symbol']}: ${data['current_price']:.2f} ({data['price_change_percentage']:.2f}%)")
    
    print("\n=== Testing Stock Data Ingestion ===")
    stock_data = ingestion.fetch_market_data('stocks', ['AAPL', 'GOOGL'], '1m')
    for data in stock_data:
        print(f"{data['symbol']}: ${data['current_price']:.2f} ({data['price_change_percentage']:.2f}%)")
    
    print("\n=== Testing E-commerce Data Ingestion ===")
    ecommerce_data = ingestion.fetch_market_data('ecommerce', ['iPhone15', 'AirPods'], '1m')
    for data in ecommerce_data:
        print(f"{data['name']}: ${data['current_price']:.2f} ({data['price_change_percentage']:.2f}%)")
    
    print(f"\n=== Cache Status ===")
    print(f"Cache entries: {len(ingestion.cache)}")