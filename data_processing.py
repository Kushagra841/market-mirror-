"""
Market Mirror - Data Processing Module
Handles data cleaning, preprocessing, and aggregation using native Python.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Union
import statistics

class DataProcessingError(Exception):
    """Custom exception for data processing errors"""
    pass

class MarketDataProcessor:
    """
    Data processing class for cleaning, normalizing, and analyzing market data.
    Implements statistical analysis and trend detection using native Python.
    """
    
    def __init__(self):
        self.processed_cache = {}
    
    def clean_data(self, raw_data: List[Dict]) -> List[Dict]:
        """
        Clean and validate raw market data
        
        Args:
            raw_data: List of raw market data dictionaries
            
        Returns:
            List of cleaned market data dictionaries
        """
        cleaned_data = []
        
        for item in raw_data:
            try:
                # Validate required fields
                required_fields = ['symbol', 'current_price', 'history']
                if not all(field in item for field in required_fields):
                    print(f"Warning: Missing required fields in {item.get('symbol', 'unknown')}")
                    continue
                
                # Clean price data
                item['current_price'] = self._clean_price(item['current_price'])
                
                # Clean historical data
                if 'history' in item and item['history']:
                    item['history'] = self._clean_historical_data(item['history'])
                
                # Ensure numeric fields are properly typed
                numeric_fields = ['price_change', 'price_change_percentage', 'volume', 'market_cap']
                for field in numeric_fields:
                    if field in item:
                        item[field] = self._clean_numeric_value(item[field])
                
                # Add timestamp if missing
                if 'last_updated' not in item:
                    item['last_updated'] = datetime.now().isoformat()
                
                cleaned_data.append(item)
                
            except Exception as e:
                print(f"Error cleaning data for {item.get('symbol', 'unknown')}: {str(e)}")
                continue
        
        return cleaned_data
    
    def _clean_price(self, price: Union[str, int, float]) -> float:
        """Clean and validate price data"""
        try:
            if isinstance(price, str):
                # Remove currency symbols and commas
                price = price.replace('$', '').replace(',', '').strip()
            
            price_float = float(price)
            
            # Validate price is positive
            if price_float <= 0:
                raise ValueError("Price must be positive")
            
            return round(price_float, 8)  # Round to 8 decimal places for crypto precision
            
        except (ValueError, TypeError):
            raise DataProcessingError(f"Invalid price value: {price}")
    
    def _clean_numeric_value(self, value: Union[str, int, float, None]) -> Optional[float]:
        """Clean and validate numeric values"""
        if value is None:
            return None
        
        try:
            if isinstance(value, str):
                value = value.replace(',', '').strip()
            return float(value)
        except (ValueError, TypeError):
            return None
    
    def _clean_historical_data(self, history: List[Dict]) -> List[Dict]:
        """Clean historical price data"""
        cleaned_history = []
        
        for point in history:
            try:
                cleaned_point = {}
                
                # Clean date
                if 'date' in point:
                    cleaned_point['date'] = self._validate_date(point['date'])
                
                # Clean price fields
                price_fields = ['price', 'open', 'high', 'low', 'close']
                for field in price_fields:
                    if field in point:
                        cleaned_point[field] = self._clean_price(point[field])
                
                # Clean volume
                if 'volume' in point:
                    cleaned_point['volume'] = self._clean_numeric_value(point['volume'])
                
                # Only add if we have essential data
                if 'date' in cleaned_point and any(field in cleaned_point for field in price_fields):
                    cleaned_history.append(cleaned_point)
                    
            except Exception as e:
                print(f"Error cleaning historical data point: {str(e)}")
                continue
        
        # Sort by date
        cleaned_history.sort(key=lambda x: x['date'])
        
        return cleaned_history
    
    def _validate_date(self, date_str: str) -> str:
        """Validate and normalize date strings"""
        try:
            # Try parsing common date formats
            for fmt in ['%Y-%m-%d', '%Y-%m-%d %H:%M:%S', '%Y-%m-%dT%H:%M:%S', '%Y-%m-%dT%H:%M:%S.%f']:
                try:
                    dt = datetime.strptime(date_str, fmt)
                    return dt.strftime('%Y-%m-%d')
                except ValueError:
                    continue
            
            raise ValueError("Unsupported date format")
            
        except Exception:
            raise DataProcessingError(f"Invalid date format: {date_str}")
    
    def resample_data(self, data: List[Dict], frequency: str = 'daily') -> List[Dict]:
        """
        Resample historical data to specified frequency
        
        Args:
            data: List of market data with history
            frequency: 'hourly', 'daily', 'weekly', 'monthly'
            
        Returns:
            List of resampled market data
        """
        resampled_data = []
        
        for item in data:
            if 'history' not in item or not item['history']:
                resampled_data.append(item)
                continue
            
            try:
                resampled_item = item.copy()
                resampled_item['history'] = self._resample_history(item['history'], frequency)
                resampled_data.append(resampled_item)
                
            except Exception as e:
                print(f"Error resampling data for {item.get('symbol', 'unknown')}: {str(e)}")
                resampled_data.append(item)  # Return original if resampling fails
        
        return resampled_data
    
    def _resample_history(self, history: List[Dict], frequency: str) -> List[Dict]:
        """Resample historical data points"""
        if not history:
            return history
        
        # Group data by time period
        grouped_data = {}
        
        for point in history:
            try:
                date = datetime.strptime(point['date'], '%Y-%m-%d')
                
                # Generate grouping key based on frequency
                if frequency == 'weekly':
                    # Group by week (Monday as start of week)
                    days_since_monday = date.weekday()
                    week_start = date - timedelta(days=days_since_monday)
                    group_key = week_start.strftime('%Y-%m-%d')
                elif frequency == 'monthly':
                    group_key = date.strftime('%Y-%m')
                else:  # daily or default
                    group_key = point['date']
                
                if group_key not in grouped_data:
                    grouped_data[group_key] = []
                
                grouped_data[group_key].append(point)
                
            except Exception as e:
                print(f"Error processing date {point.get('date', 'unknown')}: {str(e)}")
                continue
        
        # Aggregate grouped data
        resampled_history = []
        for group_key, group_points in sorted(grouped_data.items()):
            try:
                aggregated_point = self._aggregate_data_points(group_points, group_key)
                resampled_history.append(aggregated_point)
            except Exception as e:
                print(f"Error aggregating data for {group_key}: {str(e)}")
                continue
        
        return resampled_history
    
    def _aggregate_data_points(self, points: List[Dict], date_key: str) -> Dict:
        """Aggregate multiple data points into a single point"""
        if not points:
            return {}
        
        if len(points) == 1:
            return points[0]
        
        aggregated = {'date': date_key}
        
        # Price aggregation (OHLC)
        prices = []
        for point in points:
            if 'price' in point:
                prices.append(point['price'])
            elif 'close' in point:
                prices.append(point['close'])
        
        if prices:
            aggregated['open'] = prices[0]
            aggregated['close'] = prices[-1]
            aggregated['high'] = max(prices)
            aggregated['low'] = min(prices)
            aggregated['price'] = prices[-1]  # Use closing price
        
        # Volume aggregation (sum)
        volumes = [point.get('volume', 0) for point in points if 'volume' in point]
        if volumes:
            aggregated['volume'] = sum(volumes)
        
        return aggregated
    
    def calculate_technical_indicators(self, data: List[Dict]) -> List[Dict]:
        """
        Calculate technical indicators for market data
        
        Args:
            data: List of market data with historical prices
            
        Returns:
            List of market data with added technical indicators
        """
        enhanced_data = []
        
        for item in data:
            if 'history' not in item or len(item['history']) < 2:
                enhanced_data.append(item)
                continue
            
            try:
                enhanced_item = item.copy()
                history = item['history']
                
                # Extract prices for calculations
                prices = []
                for point in history:
                    if 'price' in point:
                        prices.append(point['price'])
                    elif 'close' in point:
                        prices.append(point['close'])
                
                if len(prices) < 2:
                    enhanced_data.append(item)
                    continue
                
                # Calculate indicators
                indicators = {}
                
                # Simple Moving Averages
                if len(prices) >= 5:
                    indicators['sma_5'] = statistics.mean(prices[-5:])
                if len(prices) >= 10:
                    indicators['sma_10'] = statistics.mean(prices[-10:])
                if len(prices) >= 20:
                    indicators['sma_20'] = statistics.mean(prices[-20:])
                
                # Volatility (standard deviation)
                if len(prices) >= 10:
                    recent_prices = prices[-10:]
                    indicators['volatility'] = statistics.stdev(recent_prices) if len(recent_prices) > 1 else 0
                
                # Price momentum (rate of change)
                if len(prices) >= 5:
                    old_price = prices[-5]
                    current_price = prices[-1]
                    indicators['momentum_5d'] = ((current_price - old_price) / old_price) * 100
                
                # Relative Strength Index (RSI) approximation
                if len(prices) >= 14:
                    indicators['rsi'] = self._calculate_rsi(prices[-14:])
                
                # Bollinger Bands
                if len(prices) >= 20:
                    sma_20 = statistics.mean(prices[-20:])
                    std_20 = statistics.stdev(prices[-20:])
                    indicators['bb_upper'] = sma_20 + (2 * std_20)
                    indicators['bb_lower'] = sma_20 - (2 * std_20)
                    indicators['bb_middle'] = sma_20
                
                enhanced_item['technical_indicators'] = indicators
                enhanced_data.append(enhanced_item)
                
            except Exception as e:
                print(f"Error calculating indicators for {item.get('symbol', 'unknown')}: {str(e)}")
                enhanced_data.append(item)
        
        return enhanced_data
    
    def _calculate_rsi(self, prices: List[float]) -> float:
        """Calculate Relative Strength Index"""
        if len(prices) < 2:
            return 50.0  # Neutral RSI
        
        gains = []
        losses = []
        
        for i in range(1, len(prices)):
            change = prices[i] - prices[i-1]
            if change > 0:
                gains.append(change)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(change))
        
        if not gains or not losses:
            return 50.0
        
        avg_gain = statistics.mean(gains)
        avg_loss = statistics.mean(losses)
        
        if avg_loss == 0:
            return 100.0
        
        rs = avg_gain / avg_loss
        rsi = 100 - (100 / (1 + rs))
        
        return round(rsi, 2)
    
    def compare_assets(self, data: List[Dict], comparison_metrics: List[str] = None) -> Dict:
        """
        Compare multiple assets across various metrics
        
        Args:
            data: List of market data for different assets
            comparison_metrics: List of metrics to compare
            
        Returns:
            Dictionary with comparison results
        """
        if not data:
            return {}
        
        if comparison_metrics is None:
            comparison_metrics = ['price_change_percentage', 'volatility', 'volume', 'momentum_5d']
        
        comparison_result = {
            'timestamp': datetime.now().isoformat(),
            'asset_count': len(data),
            'comparison_metrics': comparison_metrics,
            'rankings': {},
            'statistics': {}
        }
        
        # Calculate rankings for each metric
        for metric in comparison_metrics:
            rankings = []
            
            for item in data:
                value = None
                
                if metric in item:
                    value = item[metric]
                elif 'technical_indicators' in item and metric in item['technical_indicators']:
                    value = item['technical_indicators'][metric]
                
                if value is not None:
                    rankings.append({
                        'symbol': item.get('symbol', 'unknown'),
                        'name': item.get('name', item.get('symbol', 'unknown')),
                        'value': value
                    })
            
            # Sort by value (descending for most metrics)
            reverse_sort = metric not in ['volatility']  # Lower volatility is better
            rankings.sort(key=lambda x: x['value'], reverse=reverse_sort)
            
            comparison_result['rankings'][metric] = rankings
        
        # Calculate summary statistics
        for metric in comparison_metrics:
            values = []
            for item in data:
                value = None
                
                if metric in item:
                    value = item[metric]
                elif 'technical_indicators' in item and metric in item['technical_indicators']:
                    value = item['technical_indicators'][metric]
                
                if value is not None:
                    values.append(value)
            
            if values:
                comparison_result['statistics'][metric] = {
                    'mean': statistics.mean(values),
                    'median': statistics.median(values),
                    'min': min(values),
                    'max': max(values),
                    'std_dev': statistics.stdev(values) if len(values) > 1 else 0
                }
        
        return comparison_result
    
    def detect_anomalies(self, data: List[Dict], threshold_std: float = 2.0) -> List[Dict]:
        """
        Detect price anomalies using statistical methods
        
        Args:
            data: List of market data
            threshold_std: Number of standard deviations for anomaly detection
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        for item in data:
            if 'history' not in item or len(item['history']) < 10:
                continue
            
            try:
                # Extract prices
                prices = []
                dates = []
                
                for point in item['history']:
                    if 'price' in point and 'date' in point:
                        prices.append(point['price'])
                        dates.append(point['date'])
                    elif 'close' in point and 'date' in point:
                        prices.append(point['close'])
                        dates.append(point['date'])
                
                if len(prices) < 10:
                    continue
                
                # Calculate price changes
                price_changes = []
                for i in range(1, len(prices)):
                    change_pct = ((prices[i] - prices[i-1]) / prices[i-1]) * 100
                    price_changes.append(change_pct)
                
                if len(price_changes) < 5:
                    continue
                
                # Calculate statistics
                mean_change = statistics.mean(price_changes)
                std_change = statistics.stdev(price_changes)
                
                # Detect anomalies
                for i, change in enumerate(price_changes):
                    z_score = abs((change - mean_change) / std_change) if std_change > 0 else 0
                    
                    if z_score > threshold_std:
                        anomalies.append({
                            'symbol': item.get('symbol', 'unknown'),
                            'date': dates[i+1],  # +1 because price_changes is offset by 1
                            'price': prices[i+1],
                            'price_change_pct': change,
                            'z_score': z_score,
                            'severity': 'high' if z_score > 3 else 'medium',
                            'type': 'spike' if change > 0 else 'drop'
                        })
                
            except Exception as e:
                print(f"Error detecting anomalies for {item.get('symbol', 'unknown')}: {str(e)}")
                continue
        
        # Sort anomalies by severity and date
        anomalies.sort(key=lambda x: (x['z_score'], x['date']), reverse=True)
        
        return anomalies

# Example usage and testing
if __name__ == "__main__":
    # Sample data for testing
    sample_data = [
        {
            'symbol': 'BTC',
            'name': 'Bitcoin',
            'current_price': 65000.0,
            'price_change': 2000.0,
            'price_change_percentage': 3.17,
            'volume': 28000000000,
            'history': [
                {'date': '2024-01-01', 'price': 111500.0, 'volume': 25000000000},
                {'date': '2024-01-02', 'price': 111000.0, 'volume': 26000000000},
                {'date': '2024-01-03', 'price': 112000.0, 'volume': 28000000000},
            ]
        }
    ]
    
    # Initialize processor
    processor = MarketDataProcessor()
    
    # Test data cleaning
    print("=== Testing Data Cleaning ===")
    cleaned_data = processor.clean_data(sample_data)
    print(f"Cleaned {len(cleaned_data)} items")
    
    # Test technical indicators
    print("\n=== Testing Technical Indicators ===")
    enhanced_data = processor.calculate_technical_indicators(cleaned_data)
    for item in enhanced_data:
        if 'technical_indicators' in item:
            print(f"{item['symbol']}: {item['technical_indicators']}")
    
    print("\n=== Testing Anomaly Detection ===")
    anomalies = processor.detect_anomalies(enhanced_data)
    print(f"Detected {len(anomalies)} anomalies")