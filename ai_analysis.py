"""
Market Mirror - AI Analysis Module
Provides AI-powered trend analysis, insights, and recommendations.
"""

import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple
import statistics
import re

class AIAnalysisError(Exception):
    """Custom exception for AI analysis errors"""
    pass

class MarketAIAnalyzer:
    """
    AI-powered market analysis class providing trend detection,
    natural language insights, and investment recommendations.
    """
    
    def __init__(self):
        self.analysis_cache = {}
        self.trend_patterns = self._initialize_trend_patterns()
        self.sentiment_keywords = self._initialize_sentiment_keywords()
    
    def _initialize_trend_patterns(self) -> Dict:
        """Initialize trend pattern recognition rules"""
        return {
            'bullish_patterns': [
                {'name': 'Strong Uptrend', 'conditions': {'momentum_5d': (5, 100), 'rsi': (50, 70)}},
                {'name': 'Breakout', 'conditions': {'price_vs_sma_20': (1.05, 2.0)}},
                {'name': 'Recovery Rally', 'conditions': {'price_change_percentage': (3, 15), 'volatility': (0, 10)}}
            ],
            'bearish_patterns': [
                {'name': 'Strong Downtrend', 'conditions': {'momentum_5d': (-100, -5), 'rsi': (30, 50)}},
                {'name': 'Breakdown', 'conditions': {'price_vs_sma_20': (0.5, 0.95)}},
                {'name': 'Selloff', 'conditions': {'price_change_percentage': (-20, -5), 'volume_surge': True}}
            ],
            'neutral_patterns': [
                {'name': 'Sideways Consolidation', 'conditions': {'volatility': (0, 5), 'momentum_5d': (-2, 2)}},
                {'name': 'Range Bound', 'conditions': {'rsi': (40, 60), 'price_change_percentage': (-2, 2)}}
            ]
        }
    
    def _initialize_sentiment_keywords(self) -> Dict:
        """Initialize sentiment analysis keywords"""
        return {
            'positive': ['surge', 'rally', 'bullish', 'breakout', 'momentum', 'strong', 'growth', 'gains'],
            'negative': ['drop', 'fall', 'bearish', 'decline', 'crash', 'selloff', 'weakness', 'losses'],
            'neutral': ['stable', 'sideways', 'consolidation', 'range', 'mixed', 'uncertain']
        }
    
    def analyze_trends(self, market_data: List[Dict]) -> Dict:
        """
        Perform comprehensive trend analysis on market data
        
        Args:
            market_data: List of processed market data
            
        Returns:
            Dictionary containing trend analysis results
        """
        if not market_data:
            return {'error': 'No market data provided'}
        
        analysis_result = {
            'timestamp': datetime.now().isoformat(),
            'market_overview': self._generate_market_overview(market_data),
            'individual_analysis': [],
            'comparative_analysis': self._perform_comparative_analysis(market_data),
            'risk_assessment': self._assess_market_risk(market_data),
            'recommendations': []
        }
        
        # Analyze each asset individually
        for asset in market_data:
            try:
                individual_analysis = self._analyze_individual_asset(asset)
                analysis_result['individual_analysis'].append(individual_analysis)
            except Exception as e:
                print(f"Error analyzing {asset.get('symbol', 'unknown')}: {str(e)}")
                continue
        
        # Generate overall recommendations
        analysis_result['recommendations'] = self._generate_recommendations(
            analysis_result['market_overview'],
            analysis_result['individual_analysis'],
            analysis_result['risk_assessment']
        )
        
        return analysis_result
    
    def _generate_market_overview(self, market_data: List[Dict]) -> Dict:
        """Generate overall market overview"""
        if not market_data:
            return {}
        
        # Calculate market-wide statistics
        price_changes = [asset.get('price_change_percentage', 0) for asset in market_data]
        volumes = [asset.get('volume', 0) for asset in market_data if asset.get('volume', 0) > 0]
        
        overview = {
            'total_assets': len(market_data),
            'average_change': statistics.mean(price_changes) if price_changes else 0,
            'median_change': statistics.median(price_changes) if price_changes else 0,
            'volatility': statistics.stdev(price_changes) if len(price_changes) > 1 else 0,
            'gainers': len([x for x in price_changes if x > 0]),
            'losers': len([x for x in price_changes if x < 0]),
            'unchanged': len([x for x in price_changes if x == 0])
        }
        
        # Determine market sentiment
        if overview['average_change'] > 2:
            overview['sentiment'] = 'bullish'
            overview['sentiment_strength'] = 'strong' if overview['average_change'] > 5 else 'moderate'
        elif overview['average_change'] < -2:
            overview['sentiment'] = 'bearish'
            overview['sentiment_strength'] = 'strong' if overview['average_change'] < -5 else 'moderate'
        else:
            overview['sentiment'] = 'neutral'
            overview['sentiment_strength'] = 'weak'
        
        # Calculate momentum
        momentum_scores = []
        for asset in market_data:
            if 'technical_indicators' in asset and 'momentum_5d' in asset['technical_indicators']:
                momentum_scores.append(asset['technical_indicators']['momentum_5d'])
        
        if momentum_scores:
            overview['momentum'] = statistics.mean(momentum_scores)
        else:
            overview['momentum'] = 0
        
        return overview
    
    def _analyze_individual_asset(self, asset: Dict) -> Dict:
        """Analyze individual asset trends and patterns"""
        analysis = {
            'symbol': asset.get('symbol', 'unknown'),
            'name': asset.get('name', asset.get('symbol', 'unknown')),
            'current_price': asset.get('current_price', 0),
            'price_change_pct': asset.get('price_change_percentage', 0),
            'trend_direction': self._determine_trend_direction(asset),
            'pattern_detected': self._detect_patterns(asset),
            'strength': self._calculate_trend_strength(asset),
            'support_resistance': self._identify_support_resistance(asset),
            'sentiment_score': self._calculate_sentiment_score(asset),
            'risk_level': self._assess_asset_risk(asset)
        }
        
        # Generate natural language summary
        analysis['summary'] = self._generate_asset_summary(analysis, asset)
        
        return analysis
    
    def _determine_trend_direction(self, asset: Dict) -> str:
        """Determine the primary trend direction"""
        price_change = asset.get('price_change_percentage', 0)
        
        # Check technical indicators if available
        if 'technical_indicators' in asset:
            indicators = asset['technical_indicators']
            momentum = indicators.get('momentum_5d', 0)
            rsi = indicators.get('rsi', 50)
            
            # Strong bullish conditions
            if price_change > 3 and momentum > 5 and rsi > 60:
                return 'strong_bullish'
            # Moderate bullish conditions
            elif price_change > 1 or (momentum > 2 and rsi > 55):
                return 'bullish'
            # Strong bearish conditions
            elif price_change < -3 and momentum < -5 and rsi < 40:
                return 'strong_bearish'
            # Moderate bearish conditions
            elif price_change < -1 or (momentum < -2 and rsi < 45):
                return 'bearish'
        
        # Fallback to simple price change analysis
        if price_change > 2:
            return 'bullish'
        elif price_change < -2:
            return 'bearish'
        else:
            return 'neutral'
    
    def _detect_patterns(self, asset: Dict) -> List[str]:
        """Detect technical patterns in the asset"""
        detected_patterns = []
        
        if 'technical_indicators' not in asset:
            return detected_patterns
        
        indicators = asset['technical_indicators']
        price_change = asset.get('price_change_percentage', 0)
        
        # Check each pattern category
        for category, patterns in self.trend_patterns.items():
            for pattern in patterns:
                if self._matches_pattern(asset, pattern):
                    detected_patterns.append(pattern['name'])
        
        return detected_patterns
    
    def _matches_pattern(self, asset: Dict, pattern: Dict) -> bool:
        """Check if asset matches a specific pattern"""
        conditions = pattern['conditions']
        indicators = asset.get('technical_indicators', {})
        
        for condition, criteria in conditions.items():
            if condition == 'momentum_5d':
                value = indicators.get('momentum_5d', 0)
                if not (criteria[0] <= value <= criteria[1]):
                    return False
            
            elif condition == 'rsi':
                value = indicators.get('rsi', 50)
                if not (criteria[0] <= value <= criteria[1]):
                    return False
            
            elif condition == 'price_vs_sma_20':
                sma_20 = indicators.get('sma_20')
                if sma_20:
                    ratio = asset.get('current_price', 0) / sma_20
                    if not (criteria[0] <= ratio <= criteria[1]):
                        return False
                else:
                    return False
            
            elif condition == 'price_change_percentage':
                value = asset.get('price_change_percentage', 0)
                if not (criteria[0] <= value <= criteria[1]):
                    return False
            
            elif condition == 'volatility':
                value = indicators.get('volatility', 0)
                if not (criteria[0] <= value <= criteria[1]):
                    return False
            
            elif condition == 'volume_surge':
                # Simple volume analysis - would need historical comparison
                return True  # Simplified for demo
        
        return True
    
    def _calculate_trend_strength(self, asset: Dict) -> str:
        """Calculate the strength of the current trend"""
        price_change = abs(asset.get('price_change_percentage', 0))
        
        if 'technical_indicators' in asset:
            volatility = asset['technical_indicators'].get('volatility', 0)
            momentum = abs(asset['technical_indicators'].get('momentum_5d', 0))
            
            # Strong trend: significant price change with low volatility and high momentum
            if price_change > 5 and volatility < 10 and momentum > 5:
                return 'strong'
            # Moderate trend
            elif price_change > 2 and volatility < 15:
                return 'moderate'
        
        # Weak trend
        if price_change > 1:
            return 'weak'
        else:
            return 'very_weak'
    
    def _identify_support_resistance(self, asset: Dict) -> Dict:
        """Identify potential support and resistance levels"""
        if 'history' not in asset or len(asset['history']) < 10:
            return {}
        
        # Extract recent prices
        prices = []
        for point in asset['history'][-20:]:  # Last 20 data points
            if 'price' in point:
                prices.append(point['price'])
            elif 'close' in point:
                prices.append(point['close'])
        
        if len(prices) < 10:
            return {}
        
        current_price = asset.get('current_price', prices[-1])
        
        # Simple support/resistance calculation
        recent_high = max(prices)
        recent_low = min(prices)
        
        # Calculate potential levels based on recent ranges
        resistance_levels = []
        support_levels = []
        
        # Resistance: prices above current
        for price in prices:
            if price > current_price * 1.02:  # At least 2% above current
                resistance_levels.append(price)
        
        # Support: prices below current
        for price in prices:
            if price < current_price * 0.98:  # At least 2% below current
                support_levels.append(price)
        
        return {
            'nearest_resistance': min(resistance_levels) if resistance_levels else recent_high,
            'nearest_support': max(support_levels) if support_levels else recent_low,
            'recent_high': recent_high,
            'recent_low': recent_low
        }
    
    def _calculate_sentiment_score(self, asset: Dict) -> float:
        """Calculate sentiment score based on various factors"""
        score = 0.5  # Neutral starting point
        
        # Price change impact
        price_change = asset.get('price_change_percentage', 0)
        score += (price_change / 100) * 0.3  # 30% weight for price change
        
        # Technical indicators impact
        if 'technical_indicators' in asset:
            indicators = asset['technical_indicators']
            
            # RSI impact
            rsi = indicators.get('rsi', 50)
            if rsi > 70:
                score += 0.1  # Overbought (negative for sentiment)
            elif rsi < 30:
                score -= 0.1  # Oversold (positive for sentiment)
            
            # Momentum impact
            momentum = indicators.get('momentum_5d', 0)
            score += (momentum / 100) * 0.2  # 20% weight for momentum
        
        # Volume impact (simplified)
        volume = asset.get('volume', 0)
        if volume > 0:
            score += 0.05  # Positive volume impact
        
        # Clamp score between 0 and 1
        return max(0, min(1, score))
    
    def _assess_asset_risk(self, asset: Dict) -> str:
        """Assess risk level for individual asset"""
        risk_factors = []
        
        # Volatility risk
        if 'technical_indicators' in asset:
            volatility = asset['technical_indicators'].get('volatility', 0)
            if volatility > 20:
                risk_factors.append('high_volatility')
            elif volatility > 10:
                risk_factors.append('moderate_volatility')
        
        # Price change risk
        price_change = abs(asset.get('price_change_percentage', 0))
        if price_change > 10:
            risk_factors.append('high_price_movement')
        
        # Determine overall risk level
        if len(risk_factors) >= 2 or 'high_volatility' in risk_factors:
            return 'high'
        elif len(risk_factors) == 1:
            return 'medium'
        else:
            return 'low'
    
    def _perform_comparative_analysis(self, market_data: List[Dict]) -> Dict:
        """Perform comparative analysis across assets"""
        if len(market_data) < 2:
            return {}
        
        # Performance comparison
        performance_ranking = sorted(
            market_data,
            key=lambda x: x.get('price_change_percentage', 0),
            reverse=True
        )
        
        # Volatility comparison
        volatility_ranking = []
        for asset in market_data:
            volatility = 0
            if 'technical_indicators' in asset:
                volatility = asset['technical_indicators'].get('volatility', 0)
            volatility_ranking.append({
                'symbol': asset.get('symbol', 'unknown'),
                'volatility': volatility
            })
        
        volatility_ranking.sort(key=lambda x: x['volatility'])
        
        return {
            'best_performer': {
                'symbol': performance_ranking[0].get('symbol', 'unknown'),
                'change': performance_ranking[0].get('price_change_percentage', 0)
            },
            'worst_performer': {
                'symbol': performance_ranking[-1].get('symbol', 'unknown'),
                'change': performance_ranking[-1].get('price_change_percentage', 0)
            },
            'most_stable': {
                'symbol': volatility_ranking[0]['symbol'],
                'volatility': volatility_ranking[0]['volatility']
            },
            'most_volatile': {
                'symbol': volatility_ranking[-1]['symbol'],
                'volatility': volatility_ranking[-1]['volatility']
            }
        }
    
    def _assess_market_risk(self, market_data: List[Dict]) -> Dict:
        """Assess overall market risk"""
        if not market_data:
            return {}
        
        # Calculate risk metrics
        price_changes = [asset.get('price_change_percentage', 0) for asset in market_data]
        volatilities = []
        
        for asset in market_data:
            if 'technical_indicators' in asset:
                vol = asset['technical_indicators'].get('volatility', 0)
                volatilities.append(vol)
        
        # Market risk assessment
        avg_volatility = statistics.mean(volatilities) if volatilities else 0
        price_dispersion = statistics.stdev(price_changes) if len(price_changes) > 1 else 0
        
        risk_level = 'low'
        if avg_volatility > 15 or price_dispersion > 10:
            risk_level = 'high'
        elif avg_volatility > 8 or price_dispersion > 5:
            risk_level = 'medium'
        
        return {
            'overall_risk_level': risk_level,
            'average_volatility': avg_volatility,
            'price_dispersion': price_dispersion,
            'risk_factors': self._identify_risk_factors(market_data)
        }
    
    def _identify_risk_factors(self, market_data: List[Dict]) -> List[str]:
        """Identify specific risk factors in the market"""
        risk_factors = []
        
        # High volatility assets
        high_vol_count = 0
        for asset in market_data:
            if 'technical_indicators' in asset:
                if asset['technical_indicators'].get('volatility', 0) > 15:
                    high_vol_count += 1
        
        if high_vol_count / len(market_data) > 0.5:
            risk_factors.append('widespread_high_volatility')
        
        # Market correlation (simplified)
        price_changes = [asset.get('price_change_percentage', 0) for asset in market_data]
        if all(change > 5 for change in price_changes):
            risk_factors.append('overheating_market')
        elif all(change < -5 for change in price_changes):
            risk_factors.append('market_selloff')
        
        return risk_factors
    
    def _generate_recommendations(self, market_overview: Dict, individual_analyses: List[Dict], risk_assessment: Dict) -> List[Dict]:
        """Generate AI-powered investment recommendations"""
        recommendations = []
        
        # Market-level recommendations
        market_sentiment = market_overview.get('sentiment', 'neutral')
        risk_level = risk_assessment.get('overall_risk_level', 'medium')
        
        if market_sentiment == 'bullish' and risk_level == 'low':
            recommendations.append({
                'type': 'market_strategy',
                'action': 'aggressive_growth',
                'confidence': 'high',
                'reasoning': 'Strong bullish sentiment with low risk environment favors growth strategies'
            })
        elif market_sentiment == 'bearish':
            recommendations.append({
                'type': 'market_strategy',
                'action': 'defensive',
                'confidence': 'medium',
                'reasoning': 'Bearish sentiment suggests defensive positioning and risk management'
            })
        
        # Asset-specific recommendations
        for analysis in individual_analyses:
            symbol = analysis['symbol']
            trend = analysis['trend_direction']
            risk = analysis['risk_level']
            sentiment = analysis['sentiment_score']
            
            if trend == 'strong_bullish' and risk == 'low':
                recommendations.append({
                    'type': 'asset_specific',
                    'symbol': symbol,
                    'action': 'buy',
                    'confidence': 'high',
                    'reasoning': f'{symbol} shows strong bullish trend with low risk profile'
                })
            elif trend == 'strong_bearish' or risk == 'high':
                recommendations.append({
                    'type': 'asset_specific',
                    'symbol': symbol,
                    'action': 'sell_or_avoid',
                    'confidence': 'medium',
                    'reasoning': f'{symbol} shows concerning technical signals or high risk'
                })
            elif trend == 'neutral' and risk == 'low':
                recommendations.append({
                    'type': 'asset_specific',
                    'symbol': symbol,
                    'action': 'hold',
                    'confidence': 'medium',
                    'reasoning': f'{symbol} in consolidation phase with manageable risk'
                })
        
        return recommendations
    
    def _generate_asset_summary(self, analysis: Dict, asset: Dict) -> str:
        """Generate natural language summary for an asset"""
        symbol = analysis['symbol']
        price_change = analysis['price_change_pct']
        trend = analysis['trend_direction']
        patterns = analysis['pattern_detected']
        
        # Start with price movement
        if price_change > 5:
            movement_desc = f"surged {price_change:.1f}%"
        elif price_change > 1:
            movement_desc = f"gained {price_change:.1f}%"
        elif price_change < -5:
            movement_desc = f"plummeted {abs(price_change):.1f}%"
        elif price_change < -1:
            movement_desc = f"declined {abs(price_change):.1f}%"
        else:
            movement_desc = f"remained relatively stable with {price_change:.1f}% change"
        
        # Add trend context
        trend_context = ""
        if 'strong' in trend:
            trend_context = " showing strong momentum"
        elif trend != 'neutral':
            trend_context = f" in a {trend.replace('_', ' ')} trend"
        
        # Add pattern information
        pattern_info = ""
        if patterns:
            pattern_info = f" Pattern detected: {', '.join(patterns)}."
        
        # Add risk context
        risk_context = ""
        if analysis['risk_level'] == 'high':
            risk_context = " Exercise caution due to elevated risk levels."
        elif analysis['risk_level'] == 'low':
            risk_context = " Risk profile appears manageable."
        
        summary = f"{symbol} {movement_desc}{trend_context}.{pattern_info}{risk_context}"
        
        return summary
    
    def generate_market_report(self, analysis_result: Dict) -> str:
        """Generate comprehensive natural language market report"""
        if not analysis_result:
            return "No analysis data available."
        
        report_sections = []
        
        # Market overview section
        market_overview = analysis_result.get('market_overview', {})
        if market_overview:
            sentiment = market_overview.get('sentiment', 'neutral')
            avg_change = market_overview.get('average_change', 0)
            gainers = market_overview.get('gainers', 0)
            losers = market_overview.get('losers', 0)
            
            overview_text = f"Market sentiment is {sentiment} with an average change of {avg_change:.2f}%. "
            overview_text += f"Out of {market_overview.get('total_assets', 0)} assets tracked, "
            overview_text += f"{gainers} are showing gains while {losers} are in decline."
            
            report_sections.append(f"**Market Overview**: {overview_text}")
        
        # Individual asset highlights
        individual_analyses = analysis_result.get('individual_analysis', [])
        if individual_analyses:
            # Best and worst performers
            best_performer = max(individual_analyses, key=lambda x: x.get('price_change_pct', 0))
            worst_performer = min(individual_analyses, key=lambda x: x.get('price_change_pct', 0))
            
            highlights = f"**Performance Highlights**: {best_performer['symbol']} leads with "
            highlights += f"{best_performer['price_change_pct']:.2f}% gains, while "
            highlights += f"{worst_performer['symbol']} lags with {worst_performer['price_change_pct']:.2f}% change."
            
            report_sections.append(highlights)
        
        # Risk assessment
        risk_assessment = analysis_result.get('risk_assessment', {})
        if risk_assessment:
            risk_level = risk_assessment.get('overall_risk_level', 'medium')
            risk_text = f"**Risk Assessment**: Current market risk level is {risk_level}. "
            
            risk_factors = risk_assessment.get('risk_factors', [])
            if risk_factors:
                risk_text += f"Key concerns include: {', '.join(risk_factors)}."
            else:
                risk_text += "No significant risk factors identified."
            
            report_sections.append(risk_text)
        
        # Recommendations summary
        recommendations = analysis_result.get('recommendations', [])
        if recommendations:
            rec_text = "**Recommendations**: "
            market_recs = [r for r in recommendations if r['type'] == 'market_strategy']
            if market_recs:
                rec_text += f"Market strategy: {market_recs[0]['action'].replace('_', ' ')}. "
            
            asset_recs = [r for r in recommendations if r['type'] == 'asset_specific']
            if asset_recs:
                buy_recs = [r for r in asset_recs if r['action'] == 'buy']
                if buy_recs:
                    symbols = [r['symbol'] for r in buy_recs]
                    rec_text += f"Consider buying: {', '.join(symbols)}. "
            
            report_sections.append(rec_text)
        
        # Combine all sections
        full_report = "\n\n".join(report_sections)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        full_report = f"# Market Analysis Report - {timestamp}\n\n{full_report}"
        
        return full_report

# Example usage and testing
if __name__ == "__main__":
    # Sample processed market data for testing
    sample_data = [
        {
            'symbol': 'BTC',
            'name': 'Bitcoin',
            'current_price': 65000.0,
            'price_change_percentage': 5.2,
            'volume': 28000000000,
            'technical_indicators': {
                'sma_5': 63000.0,
                'sma_20': 60000.0,
                'volatility': 12.5,
                'momentum_5d': 8.2,
                'rsi': 68.0
            },
            'history': [
                {'date': '2024-01-01', 'price': 60000.0},
                {'date': '2024-01-02', 'price': 62000.0},
                {'date': '2024-01-03', 'price': 65000.0}
            ]
        },
        {
            'symbol': 'ETH',
            'name': 'Ethereum',
            'current_price': 3200.0,
            'price_change_percentage': -2.1,
            'volume': 15000000000,
            'technical_indicators': {
                'sma_5': 3250.0,
                'sma_20': 3100.0,
                'volatility': 8.3,
                'momentum_5d': -1.5,
                'rsi': 45.0
            },
            'history': [
                {'date': '2024-01-01', 'price': 3100.0},
                {'date': '2024-01-02', 'price': 3250.0},
                {'date': '2024-01-03', 'price': 3200.0}
            ]
        }
    ]
    
    # Initialize AI analyzer
    analyzer = MarketAIAnalyzer()
    
    # Perform analysis
    print("=== AI Market Analysis ===")
    analysis_result = analyzer.analyze_trends(sample_data)
    
    # Print market overview
    print("\nMarket Overview:")
    market_overview = analysis_result.get('market_overview', {})
    for key, value in market_overview.items():
        print(f"  {key}: {value}")
    
    # Print individual analyses
    print("\nIndividual Asset Analysis:")
    for analysis in analysis_result.get('individual_analysis', []):
        print(f"\n{analysis['symbol']}:")
        print(f"  Trend: {analysis['trend_direction']}")
        print(f"  Patterns: {analysis['pattern_detected']}")
        print(f"  Summary: {analysis['summary']}")
    
    # Print recommendations
    print("\nRecommendations:")
    for rec in analysis_result.get('recommendations', []):
        print(f"  {rec['symbol'] if 'symbol' in rec else 'Market'}: {rec['action']} ({rec['confidence']} confidence)")
        print(f"    Reasoning: {rec['reasoning']}")
    
    # Generate and print full report
    print("\n" + "="*50)
    print("FULL MARKET REPORT")
    print("="*50)
    report = analyzer.generate_market_report(analysis_result)
    print(report)