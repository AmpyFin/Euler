"""
System client that orchestrates market analysis.
"""
import os
import sys
from pathlib import Path
import time
from datetime import datetime
import socket
import threading
from typing import Optional, Dict, List
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                           QHBoxLayout, QLabel, QTabWidget, QFrame, QTextEdit,
                           QScrollArea)
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal
import matplotlib
matplotlib.use('Qt5Agg')
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
import numpy as np

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from clients.fetch_client import FetchClient, MarketData
from clients.processing_client import ProcessingClient, ProcessedData
from clients.inference_client import InferenceClient, MarketAnalysis
from clients.logging_config import system_logger as logger

class AnalysisWorker(QThread):
    """Worker thread for running analysis cycles."""
    analysisComplete = pyqtSignal(object)  # Simplified signal - we'll handle latencies in the main class
    
    def __init__(self, system_client):
        super().__init__()
        self.system_client = system_client
        self.running = True
    
    def run(self):
        """Run analysis cycles continuously."""
        while self.running:
            try:
                logger.info("Worker thread: Running analysis cycle")
                analysis = self.system_client.run_analysis_cycle()
                if analysis:
                    logger.info("Worker thread: Analysis complete, emitting signal")
                    self.analysisComplete.emit(analysis)
                else:
                    logger.info("Worker thread: Analysis returned None")
            except Exception as e:
                logger.error(f"Error in analysis cycle: {str(e)}")
            
            # Sleep for 60 seconds
            for _ in range(60):
                if not self.running:
                    break
                QThread.sleep(1)
    
    def stop(self):
        """Stop the worker thread."""
        self.running = False

class SystemGUI(QMainWindow):
    """GUI for displaying market analysis results."""
    
    def __init__(self, inference_client):
        """Initialize GUI with reference to inference client for weight calculations."""
        super().__init__()
        self.setWindowTitle("Euler Market Analysis")
        self.setGeometry(100, 100, 1400, 900)
        
        # Store inference client reference
        self.inference_client = inference_client
        
        # Store historical data for graphs
        self.history = {
            'scores': [],
            'regimes': [],
            'timestamps': [],
            'latencies': {},
            'indicator_data': {}
        }
        
        # Create central widget and main layout
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QVBoxLayout(central_widget)
        
        # Create tab widget
        self.tabs = QTabWidget()
        layout.addWidget(self.tabs)
        
        # Setup tabs
        self._setup_overview_tab()
        self._setup_details_tab()
        
        logger.info("GUI initialized")
    
    def _setup_overview_tab(self):
        """Setup the overview tab with main score and graphs."""
        overview_tab = QWidget()
        layout = QVBoxLayout(overview_tab)
        
        # Market status frame
        status_frame = QFrame()
        status_frame.setFrameStyle(QFrame.StyledPanel)
        status_layout = QVBoxLayout(status_frame)
        
        self.score_label = QLabel("Market Risk Score: --")
        self.score_label.setStyleSheet("font-size: 24px; font-weight: bold;")
        status_layout.addWidget(self.score_label)
        
        self.regime_label = QLabel("Current Regime: --")
        self.regime_label.setStyleSheet("font-size: 20px; font-weight: bold;")
        status_layout.addWidget(self.regime_label)
        
        self.timestamp_label = QLabel("Last Update: --")
        self.timestamp_label.setStyleSheet("font-size: 12px;")
        status_layout.addWidget(self.timestamp_label)
        
        layout.addWidget(status_frame)
        
        # Score history graph
        graph_frame = QFrame()
        graph_frame.setFrameStyle(QFrame.StyledPanel)
        graph_layout = QVBoxLayout(graph_frame)
        
        self.score_fig = Figure(figsize=(12, 4))
        self.score_ax = self.score_fig.add_subplot(111)
        self.score_canvas = FigureCanvasQTAgg(self.score_fig)
        graph_layout.addWidget(self.score_canvas)
        
        layout.addWidget(graph_frame)
        
        # Top contributors
        contributors_frame = QFrame()
        contributors_frame.setFrameStyle(QFrame.StyledPanel)
        contributors_layout = QVBoxLayout(contributors_frame)
        
        contributors_label = QLabel("Top Contributing Indicators")
        contributors_label.setStyleSheet("font-size: 14px; font-weight: bold;")
        contributors_layout.addWidget(contributors_label)
        
        self.contributors_text = QTextEdit()
        self.contributors_text.setReadOnly(True)
        self.contributors_text.setStyleSheet("font-family: monospace;")
        contributors_layout.addWidget(self.contributors_text)
        
        layout.addWidget(contributors_frame)
        
        self.tabs.addTab(overview_tab, "Overview")
    
    def _setup_details_tab(self):
        """Setup the details tab with individual indicator information."""
        details_tab = QWidget()
        layout = QVBoxLayout(details_tab)
        
        # Create scroll area for indicators
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Create container widget for indicators
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        scroll.setWidget(self.details_widget)
        
        # Store frames for each indicator
        self.indicator_frames = {}
        
        self.tabs.addTab(details_tab, "Indicator Details")
    

    
    def _create_indicator_frame(self, name: str):
        """Create or get a frame for an indicator."""
        if name not in self.indicator_frames:
            frame = QFrame()
            frame.setFrameStyle(QFrame.StyledPanel)
            self.details_layout.addWidget(frame)
            
            layout = QVBoxLayout(frame)
            
            # Title
            title = QLabel(name)
            title.setStyleSheet("font-size: 14px; font-weight: bold;")
            layout.addWidget(title)
            
            # Graph
            fig = Figure(figsize=(12, 3))
            ax = fig.add_subplot(111)
            canvas = FigureCanvasQTAgg(fig)
            layout.addWidget(canvas)
            
            # Metrics
            metrics_frame = QFrame()
            metrics_layout = QHBoxLayout(metrics_frame)
            
            raw_label = QLabel("Raw Value: --")
            metrics_layout.addWidget(raw_label)
            
            score_label = QLabel("Risk Score: --")
            metrics_layout.addWidget(score_label)
            
            weight_label = QLabel("Weight: --")
            metrics_layout.addWidget(weight_label)
            
            contrib_label = QLabel("Contribution: --")
            metrics_layout.addWidget(contrib_label)
            
            layout.addWidget(metrics_frame)
            
            self.indicator_frames[name] = {
                'frame': frame,
                'fig': fig,
                'ax': ax,
                'canvas': canvas,
                'raw_label': raw_label,
                'score_label': score_label,
                'weight_label': weight_label,
                'contrib_label': contrib_label
            }
        
        return self.indicator_frames[name]
    
    def _update_score_graph(self):
        """Update the main score history graph."""
        self.score_ax.clear()
        if len(self.history['timestamps']) > 0:
            self.score_ax.plot(self.history['timestamps'], self.history['scores'], 'b-', linewidth=2)
            self.score_ax.set_title('Market Risk Score History')
            self.score_ax.set_ylabel('Risk Score')
            self.score_ax.grid(True)
            for label in self.score_ax.get_xticklabels():
                label.set_rotation(45)
            self.score_fig.tight_layout()
            self.score_canvas.draw()
    

    
    def update_display(self, analysis):
        """Update the GUI with new analysis results."""
        try:
            # Store history
            now = datetime.now()
            self.history['scores'].append(analysis.score)
            self.history['regimes'].append(analysis.regime.label)
            self.history['timestamps'].append(now)
            
            # Update indicator data
            for name, data in analysis.data.items():
                if name not in self.history['indicator_data']:
                    self.history['indicator_data'][name] = {
                        'raw_values': [],
                        'scores': [],
                        'timestamps': []
                    }
                self.history['indicator_data'][name]['raw_values'].append(data.raw_value)
                self.history['indicator_data'][name]['scores'].append(data.score)
                self.history['indicator_data'][name]['timestamps'].append(now)
            
            # Update displays
            # Update overview tab
            self.score_label.setText(f"Market Risk Score: {analysis.score:.2f}")
            self.regime_label.setText(f"Current Regime: {analysis.regime.label}")
            self.timestamp_label.setText(f"Last Update: {now.strftime('%Y-%m-%d %H:%M:%S')}")
            
            # Update score graph
            self._update_score_graph()
            
            # Calculate total weight with guard against zero
            total_weight = sum(
                d.score * self.inference_client.get_indicator_weight(
                    n, d.raw_value, d.score, analysis.data
                )
                for n, d in analysis.data.items()
            ) or 1.0  # Use 1.0 if sum is zero
            
            # Update top contributors
            sorted_data = sorted(analysis.data.items(), 
                               key=lambda x: x[1].score * self.inference_client.get_indicator_weight(
                                   x[0], x[1].raw_value, x[1].score, analysis.data
                               ),
                               reverse=True)
            
            contributors_text = "Top Contributing Indicators:\n\n"
            for name, data in sorted_data[:5]:  # Show top 5
                weight = self.inference_client.get_indicator_weight(
                    name, data.raw_value, data.score, analysis.data
                )
                contribution = (data.score * weight / total_weight) * 100
                contributors_text += (
                    f"{name:30} | Score: {data.score:6.2f} | Weight: {weight:5.2f} | "
                    f"Contribution: {contribution:5.1f}%\n"
                )
            self.contributors_text.setText(contributors_text)
            
            # Update details tab
            for name, data in sorted_data:
                # Update or create indicator frame
                frame_data = self._create_indicator_frame(name)
                
                # Update graph
                frame_data['ax'].clear()
                frame_data['ax'].plot(self.history['indicator_data'][name]['timestamps'],
                                    self.history['indicator_data'][name]['raw_values'], 'b-', label='Raw Value')
                frame_data['ax'].plot(self.history['indicator_data'][name]['timestamps'],
                                    self.history['indicator_data'][name]['scores'], 'r-', label='Risk Score')
                frame_data['ax'].legend()
                frame_data['ax'].grid(True)
                for label in frame_data['ax'].get_xticklabels():
                    label.set_rotation(45)
                frame_data['fig'].tight_layout()
                frame_data['canvas'].draw()
                
                # Update metrics
                weight = self.inference_client.get_indicator_weight(
                    name, data.raw_value, data.score, analysis.data
                )
                contribution = (data.score * weight / total_weight) * 100
                
                frame_data['raw_label'].setText(f"Raw Value: {data.raw_value:.2f}")
                frame_data['score_label'].setText(f"Risk Score: {data.score:.2f}")
                frame_data['weight_label'].setText(f"Weight: {weight:.2f}")
                frame_data['contrib_label'].setText(f"Contribution: {contribution:.1f}%")
            
            # Update health tab
            # TODO: Update latency graph and metrics
            
            # Update window title
            self.setWindowTitle(f"Euler Market Analysis - Score: {analysis.score:.2f} - {analysis.regime.label}")
        except Exception as e:
            logger.error(f"Error updating display: {str(e)}")
    
    def run(self):
        """Start the GUI event loop."""
        self.show()
    
    def close(self):
        """Close the GUI window."""
        self.close()

class SystemClient:
    """Client for orchestrating the market analysis system."""
    
    def __init__(self):
        """Initialize the system client."""
        logger.info("Initializing SystemClient")
        
        # Create Qt application
        self.app = QApplication.instance() or QApplication(sys.argv)
        
        # Initialize clients
        self.fetch_client = FetchClient()
        self.processing_client = ProcessingClient()
        self.inference_client = InferenceClient()
        
        # Import control settings
        sys.path.insert(0, project_root)  # Ensure project root is in path
        import control
        self.broadcast_mode = getattr(control, 'broadcast_mode', False)
        self.gui_mode = getattr(control, 'GUI_mode', False)
        self.run_continuously = getattr(control, 'run_continuously', False)
        self.broadcast_network = getattr(control, 'broadcast_network', '127.0.0.1')
        self.broadcast_port = getattr(control, 'broadcast_port', 5000)
        
        # Initialize network socket for unicast mode
        self.socket = None
        if self.broadcast_mode:
            self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            # Allow reuse of address/port
            self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            # Bind to address for sending
            self.socket.bind(('', 0))  # Bind to random port for sending
            logger.info(f"Unicast sending enabled to {self.broadcast_network}:{self.broadcast_port}")
        
        # Initialize GUI if needed
        self.gui = SystemGUI(self.inference_client) if self.gui_mode else None
        
        # Initialize worker thread
        self.worker = None
        
        logger.info("SystemClient initialized successfully")
    
    def handle_analysis_results(self, analysis):
        """Handle analysis results from worker thread."""
        try:
            logger.info("handle_analysis_results called - processing analysis")
            if self.broadcast_mode:
                logger.info("Broadcast mode enabled, calling broadcast_analysis")
                self.broadcast_analysis(analysis)
            
            if self.gui:
                self.gui.update_display(analysis)
            
            # Print to console
            logger.info("\nMarket Analysis Results:")
            logger.info("-" * 80)
            logger.info(
                f"Market Risk Score: {analysis.score:.2f} | "
                f"Current Regime: {analysis.regime.label}"
            )
            logger.info("-" * 80)
            for name, data in sorted(analysis.data.items()):
                logger.info(
                    f"{name:25} | Raw: {data.raw_value:8.2f} | "
                    f"Score: {data.score:6.2f}"
                )
            logger.info("-" * 80)
        except Exception as e:
            logger.error(f"Error handling analysis results: {str(e)}")
    
    def run(self):
        """Run the market analysis system."""
        logger.info("Starting market analysis system")
        
        try:
            if self.run_continuously:
                logger.info("Running in continuous mode")
                
                # Create and start worker thread
                self.worker = AnalysisWorker(self)
                self.worker.analysisComplete.connect(self.handle_analysis_results)
                self.worker.start()
                
                # Always start Qt event loop to handle signals
                logger.info("Starting Qt event loop")
                if self.gui:
                    logger.info("GUI mode enabled")
                    self.gui.run()
                
                # Start Qt event loop to handle worker thread signals
                self.app.exec_()
            else:
                logger.info("Running single analysis cycle")
                analysis = self.run_analysis_cycle()
                if analysis:
                    self.handle_analysis_results(analysis)
                if self.gui:
                    self.gui.run()
                    self.app.exec_()
            
        except KeyboardInterrupt:
            logger.info("Received shutdown signal")
        except Exception as e:
            logger.error(f"System error: {str(e)}")
        finally:
            if self.worker:
                self.worker.stop()
                self.worker.wait()  # Wait for thread to finish
            if self.socket:
                self.socket.close()
            if self.gui:
                self.gui.close()
            logger.info("System shutdown complete")
    
    def run_analysis_cycle(self):
        """Run one complete analysis cycle."""
        try:
            # Fetch latest data
            market_data_dict: Dict[str, MarketData] = {}
            latencies: Dict[str, float] = {}
            
            for indicator in self.fetch_client.indicators:
                try:
                    name = indicator.get_name()
                    start_time = time.time()
                    value = indicator.fetch_last_quote()
                    latency = time.time() - start_time
                    latencies[name] = latency
                    
                    market_data = MarketData(
                        indicator_name=name,
                        value=value
                    )
                    market_data_dict[name] = market_data
                    logger.info(f"Fetched {name}: {value:.2f}")
                except Exception as e:
                    logger.error(f"Error fetching {indicator.__class__.__name__}: {str(e)}")
            
            # Process all data
            processed_data_dict: Dict[str, ProcessedData] = {}
            for name, market_data in market_data_dict.items():
                try:
                    score = self.processing_client.calculate_score(name, market_data.value)
                    processed = ProcessedData(
                        indicator_name=name,
                        raw_value=market_data.value,
                        score=score,
                        timestamp=market_data.timestamp
                    )
                    processed_data_dict[name] = processed
                    logger.info(
                        f"Processed {name:25} | "
                        f"Raw: {market_data.value:8.2f} → Score: {score:6.2f}"
                    )
                except Exception as e:
                    logger.error(f"Error processing {name}: {str(e)}")
            
            # Run inference
            self.inference_client.data_buffer = processed_data_dict
            analysis = self.inference_client.analyze_market_state()
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in analysis cycle: {str(e)}")
            return None
    
    def broadcast_analysis(self, analysis: MarketAnalysis):
        """Broadcast analysis results over network in broadcast mode."""
        if not self.broadcast_mode or not self.socket:
            return
            
        try:
            message = f"EULER|{analysis.score:.2f}|{analysis.regime.label}"
            logger.info(f"Sending unicast message: {message}")
            logger.info(f"Target: {self.broadcast_network}:{self.broadcast_port}")
            bytes_sent = self.socket.sendto(
                message.encode(), 
                (self.broadcast_network, self.broadcast_port)
            )
            logger.info(f"Unicast sent successfully: {bytes_sent} bytes")
        except Exception as e:
            logger.error(f"Error sending unicast message: {str(e)}")

def main():
    """Run the market analysis system."""
    system = SystemClient()
    system.run()

if __name__ == "__main__":
    main()
