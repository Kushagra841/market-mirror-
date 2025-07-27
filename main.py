"""
Market Mirror - Main Application Entry Point
Orchestrates all modules and provides a unified interface for the market analysis tool.
"""

import sys
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import time

# Import our custom modules
from data_ingestion import MarketDataIngestion, DataIngestionError
from data_processing import MarketDataProcessor, DataProcessingError
from ai_analysis import MarketAIAnalyzer, AIAnalysisError
from alerts_engine import AlertsEngine, Alert

class MarketMirrorApp:
    """
    Main application class that coordinates all market analysis components.
    Provides a unified interface for data collection, processing, analysis, and alerting.
    """
    
    def __init__(self):
        # Initialize all modules
        self.data_ingestion = MarketDataIngestion()
        self.data_processor = MarketDataProcessor()
        self.ai_analyzer = MarketAIAnalyzer()
        self.alerts_engine = AlertsEngine()
        
        # Application state
        self.current_market_data = []
        self.current_analysis = {}
        self.last_update = None
        
        # Configuration
        self.config = {
            'auto_refresh_interval': 60,  # seconds
            'max_cache_age': 300,  # 5 minutes
            'default_symbols': {
                'crypto': ['BTC', 'ETH', 'SOL'],
                'stocks': ['AAPL', 'GOOGL', 'MSFT'],
                'ecommerce': ['iPhone15', 'AirPods', 'MacBook']
            },
            'default_timeframe': '7d'
        }
        
        print("Market Mirror initialized successfully!")
        self._print_welcome_message()
    
    def _print_welcome_message(self):
        """Print welcome message and basic instructions"""
        print("\n" + "="*60)
        print("🪞 MARKET MIRROR - AI-Powered Market Analysis Tool")
        print("="*60)
        print("Available Commands:")
        print("  analyze <market_type> <symbols> <timeframe>")
        print("  add_alert <type> <symbol> <condition> <threshold>")
        print("  view_alerts")
        print("  recommendations")
        print("  report")
        print("  help")
        print("  quit")
        print("\nExample: analyze crypto BTC,ETH,SOL 7d")
        print("="*60 + "\n")
    
    def run_analysis(self, market_type: str, symbols: List[str], timeframe: str = '7d') -> Dict:
        """
        Run complete market analysis pipeline
        
        Args:
            market_type: 'crypto', 'stocks', or 'ecommerce'
            symbols: List of symbols to analyze
            timeframe: Time period for analysis
            
        Returns:
            Complete analysis results dictionary
        """
        try:
            print(f"\n🔄 Starting analysis for {market_type.upper()} - {', '.join(symbols)} ({timeframe})")
            
            # Step 1: Data Ingestion
            print("📥 Fetching market data...")
            raw_data = self.data_ingestion.fetch_market_data(market_type, symbols, timeframe)
            
            if not raw_data:
                raise ValueError("No data retrieved from sources")
            
            print(f"✅ Retrieved data for {len(raw_data)} assets")
            
            # Step 2: Data Processing
            print("⚙️ Processing and cleaning data...")
            cleaned_data = self.data_processor.clean_data(raw_data)
            processed_data = self.data_processor.calculate_technical_indicators(cleaned_data)
            
            # Step 3: AI Analysis
            print("🧠 Running AI analysis...")
            analysis_result = self.ai_analyzer.analyze_trends(processed_data)
            
            # Step 4: Alert Checking
            triggered_alerts = self.alerts_engine.check_alerts(processed_data)
            if triggered_alerts:
                print(f"🚨 {len(triggered_alerts)} alerts triggered!")
            
            # Step 5: Generate Recommendations
            recommendations = self.alerts_engine.generate_recommendations(processed_data, analysis_result)
            
            # Update application state
            self.current_market_data = processed_data
            self.current_analysis = analysis_result
            self.last_update = datetime.now()
            
            # Compile complete results
            complete_results = {
                'timestamp': self.last_update.isoformat(),
                'market_type': market_type,
                'symbols': symbols,
                'timeframe': timeframe,
                'market_data': processed_data,
                'ai_analysis': analysis_result,
                'triggered_alerts': triggered_alerts,
                'recommendations': recommendations,
                'summary': self._generate_execution_summary(processed_data, analysis_result, triggered_alerts, recommendations)
            }
            
            print("✅ Analysis complete!")
            return complete_results
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            print(f"❌ {error_msg}")
            return {
                'error': error_msg,
                'timestamp': datetime.now().isoformat()
            }
    
    def _generate_execution_summary(self, market_data: List[Dict], analysis: Dict, alerts: List[Dict], recommendations: List[Dict]) -> Dict:
        """Generate a summary of the analysis execution"""
        market_overview = analysis.get('market_overview', {})
        
        # Performance statistics
        price_changes = [asset.get('price_change_percentage', 0) for asset in market_data]
        best_performer = max(market_data, key=lambda x: x.get('price_change_percentage', 0))
        worst_performer = min(market_data, key=lambda x: x.get('price_change_percentage', 0))
        
        # Alert statistics
        alert_priorities = {}
        for alert in alerts:
            priority = alert.get('priority', 'medium')
            alert_priorities[priority] = alert_priorities.get(priority, 0) + 1
        
        # Recommendation statistics
        rec_types = {}
        for rec in recommendations:
            rec_type = rec.get('type', 'unknown')
            rec_types[rec_type] = rec_types.get(rec_type, 0) + 1
        
        return {
            'assets_analyzed': len(market_data),
            'market_sentiment': market_overview.get('sentiment', 'neutral'),
            'average_change': market_overview.get('average_change', 0),
            'best_performer': {
                'symbol': best_performer.get('symbol', 'N/A'),
                'change': best_performer.get('price_change_percentage', 0)
            },
            'worst_performer': {
                'symbol': worst_performer.get('symbol', 'N/A'),
                'change': worst_performer.get('price_change_percentage', 0)
            },
            'alerts_triggered': len(alerts),
            'alert_breakdown': alert_priorities,
            'recommendations_generated': len(recommendations),
            'recommendation_breakdown': rec_types
        }
    
    def add_alert(self, alert_type: str, symbol: str, condition: str, threshold: float, priority: str = 'medium') -> str:
        """Add a new market alert"""
        try:
            if alert_type == 'price':
                alert_id = self.alerts_engine.add_price_alert(symbol, condition, threshold, priority)
            elif alert_type == 'change':
                alert_id = self.alerts_engine.add_percentage_change_alert(symbol, condition, threshold, '24h', priority)
            elif alert_type == 'volume':
                alert_id = self.alerts_engine.add_volume_alert(symbol, condition, threshold, priority)
            else:
                raise ValueError(f"Unsupported alert type: {alert_type}")
            
            return alert_id
            
        except Exception as e:
            print(f"❌ Failed to add alert: {str(e)}")
            return ""
    
    def view_alerts(self) -> Dict:
        """View all active alerts and recent history"""
        active_alerts = self.alerts_engine.get_active_alerts()
        alert_history = self.alerts_engine.get_alert_history(10)
        
        return {
            'active_alerts': active_alerts,
            'recent_history': alert_history,
            'total_active': len(active_alerts)
        }
    
    def get_recommendations(self) -> List[Dict]:
        """Get recent recommendations"""
        return self.alerts_engine.get_recent_recommendations(15)
    
    def generate_report(self) -> str:
        """Generate comprehensive market report"""
        if not self.current_analysis:
            return "No analysis data available. Please run an analysis first."
        
        # Generate AI report
        ai_report = self.ai_analyzer.generate_market_report(self.current_analysis)
        
        # Add execution summary
        if 'summary' in self.current_analysis:
            summary = self.current_analysis['summary']
            summary_text = f"\n## Execution Summary\n\n"
            summary_text += f"- **Assets Analyzed**: {summary['assets_analyzed']}\n"
            summary_text += f"- **Market Sentiment**: {summary['market_sentiment'].title()}\n"
            summary_text += f"- **Average Change**: {summary['average_change']:.2f}%\n"
            summary_text += f"- **Best Performer**: {summary['best_performer']['symbol']} ({summary['best_performer']['change']:.2f}%)\n"
            summary_text += f"- **Worst Performer**: {summary['worst_performer']['symbol']} ({summary['worst_performer']['change']:.2f}%)\n"
            summary_text += f"- **Alerts Triggered**: {summary['alerts_triggered']}\n"
            summary_text += f"- **Recommendations**: {summary['recommendations_generated']}\n"
            
            ai_report += summary_text
        
        return ai_report
    
    def interactive_mode(self):
        """Run the application in interactive command-line mode"""
        print("🚀 Starting interactive mode. Type 'help' for commands or 'quit' to exit.")
        
        while True:
            try:
                command = input("\nMarket Mirror > ").strip().lower()
                
                if command == 'quit' or command == 'exit':
                    print("👋 Goodbye!")
                    break
                
                elif command == 'help':
                    self._print_help()
                
                elif command.startswith('analyze'):
                    self._handle_analyze_command(command)
                
                elif command.startswith('add_alert'):
                    self._handle_add_alert_command(command)
                
                elif command in ['alerts', 'view_alerts']:
                    self._handle_view_alerts_command()
                
                elif command in ['recommendations', 'recs']:
                    self._handle_recommendations_command()
                
                elif command in ['report', 'summary']:
                    self._handle_report_command()
                
                elif command == 'clear':
                    self._handle_clear_command()
                
                elif command == 'status':
                    self._handle_status_command()
                
                else:
                    print("❓ Unknown command. Type 'help' for available commands.")
                    
            except KeyboardInterrupt:
                print("\n👋 Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error: {str(e)}")
    
    def _print_help(self):
        """Print help information"""
        print("\n📖 MARKET MIRROR COMMANDS:")
        print("-" * 40)
        print("analyze <market> <symbols> <timeframe>")
        print("  Example: analyze crypto BTC,ETH 7d")
        print("  Markets: crypto, stocks, ecommerce")
        print("  Timeframes: 1d, 7d, 1m, 3m")
        print("")
        print("add_alert <type> <symbol> <condition> <threshold>")
        print("  Example: add_alert price BTC below 60000")
        print("  Types: price, change, volume")
        print("  Conditions: above, below")
        print("")
        print("alerts          - View active alerts")
        print("recommendations - View recent recommendations")
        print("report          - Generate full market report")
        print("status          - Show application status")
        print("clear           - Clear all cached data")
        print("help            - Show this help")
        print("quit            - Exit application")
        print("-" * 40)
    
    def _handle_analyze_command(self, command: str):
        """Handle analyze command"""
        try:
            parts = command.split()
            if len(parts) < 3:
                print("❌ Usage: analyze <market_type> <symbols> [timeframe]")
                return
            
            market_type = parts[1]
            symbols_str = parts[2]
            timeframe = parts[3] if len(parts) > 3 else '7d'
            
            symbols = [s.strip().upper() for s in symbols_str.split(',')]
            
            # Validate market type
            if market_type not in ['crypto', 'stocks', 'ecommerce']:
                print("❌ Market type must be: crypto, stocks, or ecommerce")
                return
            
            # Run analysis
            results = self.run_analysis(market_type, symbols, timeframe)
            
            if 'error' in results:
                print(f"❌ Analysis failed: {results['error']}")
                return
            
            # Display summary
            summary = results.get('summary', {})
            print(f"\n📊 ANALYSIS RESULTS:")
            print(f"Market Sentiment: {summary.get('market_sentiment', 'Unknown').title()}")
            print(f"Average Change: {summary.get('average_change', 0):.2f}%")
            print(f"Best: {summary.get('best_performer', {}).get('symbol', 'N/A')} "
                  f"({summary.get('best_performer', {}).get('change', 0):.2f}%)")
            print(f"Worst: {summary.get('worst_performer', {}).get('symbol', 'N/A')} "
                  f"({summary.get('worst_performer', {}).get('change', 0):.2f}%)")
            print(f"Alerts: {summary.get('alerts_triggered', 0)}")
            print(f"Recommendations: {summary.get('recommendations_generated', 0)}")
            
        except Exception as e:
            print(f"❌ Error processing analyze command: {str(e)}")
    
    def _handle_add_alert_command(self, command: str):
        """Handle add_alert command"""
        try:
            parts = command.split()
            if len(parts) < 5:
                print("❌ Usage: add_alert <type> <symbol> <condition> <threshold>")
                return
            
            alert_type = parts[1]
            symbol = parts[2].upper()
            condition = parts[3]
            threshold = float(parts[4])
            
            alert_id = self.add_alert(alert_type, symbol, condition, threshold)
            
            if alert_id:
                print(f"✅ Alert added: {alert_id}")
            
        except Exception as e:
            print(f"❌ Error adding alert: {str(e)}")
    
    def _handle_view_alerts_command(self):
        """Handle view alerts command"""
        try:
            alerts_info = self.view_alerts()
            active = alerts_info['active_alerts']
            history = alerts_info['recent_history']
            
            print(f"\n🔔 ACTIVE ALERTS ({len(active)}):")
            if not active:
                print("  No active alerts")
            else:
                for alert in active:
                    print(f"  {alert['symbol']}: {alert['message']} (Priority: {alert['priority']})")
            
            print(f"\n📜 RECENT HISTORY ({len(history)}):")
            if not history:
                print("  No recent alerts")
            else:
                for alert in history[-5:]:  # Show last 5
                    timestamp = alert.get('triggered_at', alert.get('created_at', 'Unknown'))
                    print(f"  {alert['symbol']}: {alert['message']} ({timestamp})")
                    
        except Exception as e:
            print(f"❌ Error viewing alerts: {str(e)}")
    
    def _handle_recommendations_command(self):
        """Handle recommendations command"""
        try:
            recommendations = self.get_recommendations()
            
            print(f"\n💡 RECENT RECOMMENDATIONS ({len(recommendations)}):")
            if not recommendations:
                print("  No recent recommendations")
            else:
                for rec in recommendations[:10]:  # Show top 10
                    rec_type = rec.get('type', 'general')
                    symbol = rec.get('symbol', '')
                    recommendation = rec.get('recommendation', 'No recommendation')
                    confidence = rec.get('confidence', 'unknown')
                    
                    if symbol:
                        print(f"  {symbol}: {recommendation} (Confidence: {confidence})")
                    else:
                        print(f"  Market: {recommendation} (Confidence: {confidence})")
                    
                    reasoning = rec.get('reasoning', '')
                    if reasoning:
                        print(f"    → {reasoning}")
                    print()
                    
        except Exception as e:
            print(f"❌ Error getting recommendations: {str(e)}")
    
    def _handle_report_command(self):
        """Handle report command"""
        try:
            report = self.generate_report()
            print("\n" + "="*60)
            print(report)
            print("="*60)
            
        except Exception as e:
            print(f"❌ Error generating report: {str(e)}")
    
    def _handle_clear_command(self):
        """Handle clear command"""
        try:
            self.data_ingestion.clear_cache()
            self.alerts_engine.clear_cache()
            self.current_market_data = []
            self.current_analysis = {}
            self.last_update = None
            
            print("✅ All cached data cleared")
            
        except Exception as e:
            print(f"❌ Error clearing cache: {str(e)}")
    
    def _handle_status_command(self):
        """Handle status command"""
        try:
            print(f"\n📊 MARKET MIRROR STATUS:")
            print(f"Last Update: {self.last_update or 'Never'}")
            print(f"Active Alerts: {len(self.alerts_engine.get_active_alerts())}")
            print(f"Cached Market Data: {len(self.current_market_data)} assets")
            print(f"Analysis Available: {'Yes' if self.current_analysis else 'No'}")
            print(f"Cache Age: {(datetime.now() - self.last_update).seconds if self.last_update else 'N/A'} seconds")
            
        except Exception as e:
            print(f"❌ Error getting status: {str(e)}")

def main():
    """Main entry point for the Market Mirror application"""
    try:
        # Create and initialize the application
        app = MarketMirrorApp()
        
        # Check command line arguments
        if len(sys.argv) > 1:
            command = ' '.join(sys.argv[1:])
            print(f"Executing command: {command}")
            
            # Handle direct commands
            if command.startswith('analyze'):
                app._handle_analyze_command(command)
            else:
                print("❌ Unknown command. Available: analyze <market> <symbols> <timeframe>")
        else:
            # Run in interactive mode
            app.interactive_mode()
            
    except KeyboardInterrupt:
        print("\n👋 Application terminated by user")
    except Exception as e:
        print(f"❌ Application error: {str(e)}")
        sys.exit(1)

if __name__ == "__main__":
    main()