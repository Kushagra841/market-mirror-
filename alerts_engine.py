"""
Market Mirror - Alerts and Recommendation Engine
Handles real-time alerts, threshold monitoring, and automated notifications.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Callable, Any
import threading
import time

class AlertEngineError(Exception):
    """Custom exception for alert engine errors"""
    pass

class Alert:
    """Represents a single market alert"""
    
    def __init__(self, alert_id: str, alert_type: str, symbol: str, condition: str, 
                 threshold: float, message: str, priority: str = 'medium'):
        self.alert_id = alert_id
        self.alert_type = alert_type  # 'price', 'volume', 'change_percent', 'technical'
        self.symbol = symbol
        self.condition = condition  # 'above', 'below', 'equals'
        self.threshold = threshold
        self.message = message
        self.priority = priority  # 'low', 'medium', 'high', 'critical'
        self.created_at = datetime.now()
        self.triggered_at = None
        self.is_active = True
        self.trigger_count = 0
    
    def to_dict(self) -> Dict:
        """Convert alert to dictionary"""
        return {
            'alert_id': self.alert_id,
            'alert_type': self.alert_type,
            'symbol': self.symbol,
            'condition': self.condition,
            'threshold': self.threshold,
            'message': self.message,
            'priority': self.priority,
            'created_at': self.created_at.isoformat(),
            'triggered_at': self.triggered_at.isoformat() if self.triggered_at else None,
            'is_active': self.is_active,
            'trigger_count': self.trigger_count
        }

class AlertsEngine:
    """
    Comprehensive alerts and recommendation engine for market monitoring.
    Supports multiple alert types, custom conditions, and automated notifications.
    """
    
    def __init__(self):
        self.alerts = {}  # Dictionary of active alerts
        self.alert_history = []  # List of triggered alerts
        self.notification_handlers = []  # List of notification functions
        self.is_monitoring = False
        self.monitor_thread = None
        self.check_interval = 10  # seconds between checks
        self.recommendation_cache = {}
        
        # Initialize default notification handlers
        self._initialize_default_handlers()
    
    def _initialize_default_handlers(self):
        """Initialize default notification handlers"""
        self.notification_handlers = [
            self._console_notification_handler,
            self._log_notification_handler
        ]
    
    def add_price_alert(self, symbol: str, condition: str, threshold: float, 
                       priority: str = 'medium') -> str:
        """
        Add a price-based alert
        
        Args:
            symbol: Asset symbol (e.g., 'BTC', 'AAPL')
            condition: 'above' or 'below'
            threshold: Price threshold
            priority: Alert priority level
            
        Returns:
            Alert ID string
        """
        alert_id = f"price_{symbol}_{condition}_{threshold}_{int(time.time())}"
        
        message = f"{symbol} price {condition} ${threshold:,.2f}"
        
        alert = Alert(
            alert_id=alert_id,
            alert_type='price',
            symbol=symbol,
            condition=condition,
            threshold=threshold,
            message=message,
            priority=priority
        )
        
        self.alerts[alert_id] = alert
        print(f"Price alert added: {message}")
        
        return alert_id
    
    def add_percentage_change_alert(self, symbol: str, condition: str, threshold: float,
                                  timeframe: str = '24h', priority: str = 'medium') -> str:
        """
        Add a percentage change alert
        
        Args:
            symbol: Asset symbol
            condition: 'above' or 'below'  
            threshold: Percentage threshold (e.g., 5.0 for 5%)
            timeframe: Time period for change calculation
            priority: Alert priority level
            
        Returns:
            Alert ID string
        """
        alert_id = f"change_{symbol}_{condition}_{threshold}_{timeframe}_{int(time.time())}"
        
        direction = "gained" if condition == "above" and threshold > 0 else "lost"
        message = f"{symbol} {direction} more than {abs(threshold):.1f}% in {timeframe}"
        
        alert = Alert(
            alert_id=alert_id,
            alert_type='change_percent',
            symbol=symbol,
            condition=condition,
            threshold=threshold,
            message=message,
            priority=priority
        )
        
        self.alerts[alert_id] = alert
        print(f"Percentage change alert added: {message}")
        
        return alert_id
    
    def add_volume_alert(self, symbol: str, condition: str, threshold: float,
                        priority: str = 'medium') -> str:
        """
        Add a volume-based alert
        
        Args:
            symbol: Asset symbol
            condition: 'above' or 'below'
            threshold: Volume threshold
            priority: Alert priority level
            
        Returns:
            Alert ID string
        """
        alert_id = f"volume_{symbol}_{condition}_{threshold}_{int(time.time())}"
        
        message = f"{symbol} volume {condition} {threshold:,.0f}"
        
        alert = Alert(
            alert_id=alert_id,
            alert_type='volume',
            symbol=symbol,
            condition=condition,
            threshold=threshold,
            message=message,
            priority=priority
        )
        
        self.alerts[alert_id] = alert
        print(f"Volume alert added: {message}")
        
        return alert_id
    
    def add_technical_alert(self, symbol: str, indicator: str, condition: str, 
                           threshold: float, priority: str = 'medium') -> str:
        """
        Add a technical indicator alert
        
        Args:
            symbol: Asset symbol
            indicator: Technical indicator name (e.g., 'rsi', 'sma_20')
            condition: 'above' or 'below'
            threshold: Indicator threshold
            priority: Alert priority level
            
        Returns:
            Alert ID string
        """
        alert_id = f"tech_{symbol}_{indicator}_{condition}_{threshold}_{int(time.time())}"
        
        message = f"{symbol} {indicator.upper()} {condition} {threshold}"
        
        alert = Alert(
            alert_id=alert_id,
            alert_type='technical',
            symbol=symbol,
            condition=condition,
            threshold=threshold,
            message=f"{message} - {indicator}",
            priority=priority
        )
        
        # Store the indicator name for checking
        alert.indicator = indicator
        
        self.alerts[alert_id] = alert
        print(f"Technical alert added: {message}")
        
        return alert_id
    
    def remove_alert(self, alert_id: str) -> bool:
        """
        Remove an alert by ID
        
        Args:
            alert_id: Alert identifier
            
        Returns:
            True if alert was removed, False if not found
        """
        if alert_id in self.alerts:
            alert = self.alerts[alert_id]
            del self.alerts[alert_id]
            print(f"Alert removed: {alert.message}")
            return True
        return False
    
    def get_active_alerts(self) -> List[Dict]:
        """Get all active alerts"""
        return [alert.to_dict() for alert in self.alerts.values() if alert.is_active]
    
    def get_alert_history(self, limit: int = 50) -> List[Dict]:
        """Get recent alert history"""
        return self.alert_history[-limit:]
    
    def check_alerts(self, market_data: List[Dict]) -> List[Dict]:
        """
        Check all active alerts against current market data
        
        Args:
            market_data: List of current market data
            
        Returns:
            List of triggered alerts
        """
        triggered_alerts = []
        
        # Create a lookup dictionary for market data
        data_lookup = {item.get('symbol', ''): item for item in market_data}
        
        for alert_id, alert in list(self.alerts.items()):
            if not alert.is_active:
                continue
            
            symbol = alert.symbol
            if symbol not in data_lookup:
                continue
            
            asset_data = data_lookup[symbol]
            
            try:
                if self._check_single_alert(alert, asset_data):
                    # Alert triggered
                    alert.triggered_at = datetime.now()
                    alert.trigger_count += 1
                    
                    triggered_alert = alert.to_dict()
                    triggered_alert['current_value'] = self._get_alert_current_value(alert, asset_data)
                    
                    triggered_alerts.append(triggered_alert)
                    self.alert_history.append(triggered_alert)
                    
                    # Send notifications
                    self._send_notifications(triggered_alert)
                    
                    # Remove one-time alerts or deactivate recurring ones
                    if alert.alert_type in ['price', 'change_percent']:
                        alert.is_active = False  # One-time alert
                    
                    print(f"ALERT TRIGGERED: {alert.message}")
                
            except Exception as e:
                print(f"Error checking alert {alert_id}: {str(e)}")
                continue
        
        return triggered_alerts
    
    def _check_single_alert(self, alert: Alert, asset_data: Dict) -> bool:
        """Check if a single alert condition is met"""
        if alert.alert_type == 'price':
            current_price = asset_data.get('current_price', 0)
            return self._evaluate_condition(current_price, alert.condition, alert.threshold)
        
        elif alert.alert_type == 'change_percent':
            change_percent = asset_data.get('price_change_percentage', 0)
            return self._evaluate_condition(abs(change_percent), 'above', abs(alert.threshold))
        
        elif alert.alert_type == 'volume':
            volume = asset_data.get('volume', 0)
            return self._evaluate_condition(volume, alert.condition, alert.threshold)
        
        elif alert.alert_type == 'technical':
            if 'technical_indicators' not in asset_data:
                return False
            
            indicators = asset_data['technical_indicators']
            if not hasattr(alert, 'indicator') or alert.indicator not in indicators:
                return False
            
            indicator_value = indicators[alert.indicator]
            return self._evaluate_condition(indicator_value, alert.condition, alert.threshold)
        
        return False
    
    def _evaluate_condition(self, current_value: float, condition: str, threshold: float) -> bool:
        """Evaluate if a condition is met"""
        if condition == 'above':
            return current_value > threshold
        elif condition == 'below':
            return current_value < threshold
        elif condition == 'equals':
            return abs(current_value - threshold) < 0.01  # Small tolerance for floats
        else:
            return False
    
    def _get_alert_current_value(self, alert: Alert, asset_data: Dict) -> float:
        """Get the current value that triggered the alert"""
        if alert.alert_type == 'price':
            return asset_data.get('current_price', 0)
        elif alert.alert_type == 'change_percent':
            return asset_data.get('price_change_percentage', 0)
        elif alert.alert_type == 'volume':
            return asset_data.get('volume', 0)
        elif alert.alert_type == 'technical' and hasattr(alert, 'indicator'):
            indicators = asset_data.get('technical_indicators', {})
            return indicators.get(alert.indicator, 0)
        return 0
    
    def _send_notifications(self, triggered_alert: Dict):
        """Send notifications for triggered alert"""
        for handler in self.notification_handlers:
            try:
                handler(triggered_alert)
            except Exception as e:
                print(f"Error in notification handler: {str(e)}")
    
    def _console_notification_handler(self, alert: Dict):
        """Default console notification handler"""
        priority = alert.get('priority', 'medium').upper()
        symbol = alert.get('symbol', 'UNKNOWN')
        message = alert.get('message', 'Alert triggered')
        current_value = alert.get('current_value', 0)
        
        notification = f"[{priority}] {symbol}: {message} (Current: {current_value})"
        print(f"🚨 MARKET ALERT: {notification}")
    
    def _log_notification_handler(self, alert: Dict):
        """Log notification handler"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_entry = f"{timestamp} - Alert triggered: {alert}"
        
        # In a real implementation, this would write to a log file
        # For demo purposes, we'll just store in memory
        if not hasattr(self, 'alert_log'):
            self.alert_log = []
        self.alert_log.append(log_entry)
    
    def add_notification_handler(self, handler: Callable):
        """Add a custom notification handler"""
        self.notification_handlers.append(handler)
    
    def generate_recommendations(self, market_data: List[Dict], ai_analysis: Dict) -> List[Dict]:
        """
        Generate automated recommendations based on market data and AI analysis
        
        Args:
            market_data: Current market data
            ai_analysis: AI analysis results
            
        Returns:
            List of recommendation dictionaries
        """
        recommendations = []
        timestamp = datetime.now().isoformat()
        
        # Market-level recommendations
        market_overview = ai_analysis.get('market_overview', {})
        market_sentiment = market_overview.get('sentiment', 'neutral')
        average_change = market_overview.get('average_change', 0)
        
        if market_sentiment == 'bullish' and average_change > 3:
            recommendations.append({
                'type': 'market_strategy',
                'recommendation': 'Consider increasing market exposure',
                'confidence': 'medium',
                'reasoning': 'Strong bullish sentiment with positive momentum',
                'timestamp': timestamp,
                'priority': 'medium'
            })
        elif market_sentiment == 'bearish' and average_change < -3:
            recommendations.append({
                'type': 'market_strategy',
                'recommendation': 'Consider defensive positioning',
                'confidence': 'high',
                'reasoning': 'Bearish sentiment with negative momentum suggests caution',
                'timestamp': timestamp,
                'priority': 'high'
            })
        
        # Asset-specific recommendations
        individual_analyses = ai_analysis.get('individual_analysis', [])
        for analysis in individual_analyses:
            symbol = analysis.get('symbol', 'UNKNOWN')
            trend_direction = analysis.get('trend_direction', 'neutral')
            risk_level = analysis.get('risk_level', 'medium')
            sentiment_score = analysis.get('sentiment_score', 0.5)
            
            # Find corresponding market data
            asset_data = None
            for data in market_data:
                if data.get('symbol') == symbol:
                    asset_data = data
                    break
            
            if not asset_data:
                continue
            
            # Generate recommendations based on multiple factors
            if trend_direction == 'strong_bullish' and risk_level == 'low':
                recommendations.append({
                    'type': 'asset_specific',
                    'symbol': symbol,
                    'recommendation': 'Strong Buy',
                    'confidence': 'high',
                    'reasoning': 'Strong bullish trend with low risk profile',
                    'target_allocation': '5-10%',
                    'timestamp': timestamp,
                    'priority': 'high'
                })
            elif trend_direction == 'bullish' and sentiment_score > 0.6:
                recommendations.append({
                    'type': 'asset_specific',
                    'symbol': symbol,
                    'recommendation': 'Buy',
                    'confidence': 'medium',
                    'reasoning': 'Positive trend with good sentiment',
                    'target_allocation': '3-5%',
                    'timestamp': timestamp,
                    'priority': 'medium'
                })
            elif trend_direction == 'strong_bearish' or risk_level == 'high':
                recommendations.append({
                    'type': 'asset_specific',
                    'symbol': symbol,
                    'recommendation': 'Sell/Avoid',
                    'confidence': 'medium',
                    'reasoning': 'Negative trend or high risk profile',
                    'target_allocation': '0%',
                    'timestamp': timestamp,
                    'priority': 'medium'
                })
            elif trend_direction == 'neutral' and risk_level == 'low':
                recommendations.append({
                    'type': 'asset_specific',
                    'symbol': symbol,
                    'recommendation': 'Hold',
                    'confidence': 'low',
                    'reasoning': 'Stable conditions, maintain current position',
                    'target_allocation': 'Current',
                    'timestamp': timestamp,
                    'priority': 'low'
                })
        
        # Risk management recommendations
        risk_assessment = ai_analysis.get('risk_assessment', {})
        overall_risk = risk_assessment.get('overall_risk_level', 'medium')
        
        if overall_risk == 'high':
            recommendations.append({
                'type': 'risk_management',
                'recommendation': 'Reduce position sizes and implement stop losses',
                'confidence': 'high',
                'reasoning': 'High market risk detected across multiple assets',
                'timestamp': timestamp,
                'priority': 'high'
            })
        
        # Cache recommendations
        self.recommendation_cache[timestamp] = recommendations
        
        return recommendations
    
    def start_monitoring(self, data_source_func: Callable, ai_analysis_func: Callable):
        """
        Start continuous monitoring with alerts and recommendations
        
        Args:
            data_source_func: Function that returns current market data
            ai_analysis_func: Function that returns AI analysis
        """
        if self.is_monitoring:
            print("Monitoring already active")
            return
        
        self.is_monitoring = True
        
        def monitor_loop():
            print(f"Starting market monitoring (checking every {self.check_interval} seconds)")
            
            while self.is_monitoring:
                try:
                    # Get current market data
                    market_data = data_source_func()
                    
                    if market_data:
                        # Check alerts
                        triggered_alerts = self.check_alerts(market_data)
                        
                        # Generate AI analysis and recommendations
                        if triggered_alerts or len(self.recommendation_cache) == 0:
                            ai_analysis = ai_analysis_func(market_data)
                            recommendations = self.generate_recommendations(market_data, ai_analysis)
                            
                            if recommendations:
                                print(f"Generated {len(recommendations)} new recommendations")
                    
                except Exception as e:
                    print(f"Error in monitoring loop: {str(e)}")
                
                # Wait before next check
                time.sleep(self.check_interval)
        
        # Start monitoring in separate thread
        self.monitor_thread = threading.Thread(target=monitor_loop, daemon=True)
        self.monitor_thread.start()
    
    def stop_monitoring(self):
        """Stop continuous monitoring"""
        if self.is_monitoring:
            self.is_monitoring = False
            print("Market monitoring stopped")
    
    def get_recent_recommendations(self, limit: int = 10) -> List[Dict]:
        """Get recent recommendations"""
        all_recommendations = []
        for timestamp, recs in sorted(self.recommendation_cache.items(), reverse=True):
            all_recommendations.extend(recs)
            if len(all_recommendations) >= limit:
                break
        
        return all_recommendations[:limit]
    
    def clear_cache(self):
        """Clear all cached data"""
        self.recommendation_cache.clear()
        self.alert_history.clear()
        print("Alert engine cache cleared")

# Example usage and testing
if __name__ == "__main__":
    # Sample market data for testing
    sample_market_data = [
        {
            'symbol': 'BTC',
            'current_price': 65000.0,
            'price_change_percentage': 5.2,
            'volume': 28000000000,
            'technical_indicators': {'rsi': 68.0, 'sma_20': 60000.0}
        },
        {
            'symbol': 'ETH',
            'current_price': 3200.0,
            'price_change_percentage': -2.1,
            'volume': 15000000000,
            'technical_indicators': {'rsi': 45.0, 'sma_20': 3100.0}
        }
    ]
    
    sample_ai_analysis = {
        'market_overview': {
            'sentiment': 'bullish',
            'average_change': 1.55,
            'total_assets': 2
        },
        'individual_analysis': [
            {
                'symbol': 'BTC',
                'trend_direction': 'strong_bullish',
                'risk_level': 'low',
                'sentiment_score': 0.75
            },
            {
                'symbol': 'ETH',
                'trend_direction': 'bearish',
                'risk_level': 'medium',
                'sentiment_score': 0.35
            }
        ],
        'risk_assessment': {
            'overall_risk_level': 'medium'
        }
    }
    
    # Initialize alerts engine
    alerts_engine = AlertsEngine()
    
    # Add sample alerts
    print("=== Adding Sample Alerts ===")
    alerts_engine.add_price_alert('BTC', 'above', 70000.0, 'high')
    alerts_engine.add_price_alert('BTC', 'below', 60000.0, 'medium')
    alerts_engine.add_percentage_change_alert('ETH', 'above', 10.0, '24h', 'high')
    alerts_engine.add_technical_alert('BTC', 'rsi', 'above', 70.0, 'medium')
    
    # Test alert checking
    print("\n=== Checking Alerts ===")
    triggered = alerts_engine.check_alerts(sample_market_data)
    print(f"Triggered alerts: {len(triggered)}")
    
    # Test recommendations
    print("\n=== Generating Recommendations ===")
    recommendations = alerts_engine.generate_recommendations(sample_market_data, sample_ai_analysis)
    
    for rec in recommendations:
        print(f"  {rec['type']}: {rec['recommendation']}")
        if 'symbol' in rec:
            print(f"    Symbol: {rec['symbol']}")
        print(f"    Confidence: {rec['confidence']}, Priority: {rec['priority']}")
        print(f"    Reasoning: {rec['reasoning']}")
        print()
    
    # Display active alerts
    print("=== Active Alerts ===")
    active_alerts = alerts_engine.get_active_alerts()
    for alert in active_alerts:
        print(f"  {alert['symbol']}: {alert['message']} (Priority: {alert['priority']})")