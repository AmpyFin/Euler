"""
System client that orchestrates market analysis.
"""
import os
import sys
from pathlib import Path
import time
import queue
from datetime import datetime
import signal
import threading
from typing import Callable, Optional

# Add project root to Python path
project_root = str(Path(__file__).parent.parent)
sys.path.insert(0, project_root)

from clients.fetch_client import FetchClient
from clients.processing_client import ProcessingClient
from clients.inference_client import InferenceClient, MarketAnalysis
from clients.logging_config import system_logger as logger

class SystemClient:
    """Client for orchestrating the market analysis system."""
    
    def __init__(self, callback: Optional[Callable[[MarketAnalysis], None]] = None):
        """Initialize the system client."""
        logger.info("Initializing SystemClient")
        
        # Initialize queues
        self.fetch_queue = queue.Queue()
        self.process_queue = queue.Queue()
        self.inference_queue = queue.Queue()
        
        # Initialize clients
        self.fetch_client = FetchClient()
        self.processing_client = ProcessingClient()
        self.inference_client = InferenceClient()
        
        # Connect queues
        self.fetch_client.output_queue = self.fetch_queue
        self.processing_client.input_queue = self.fetch_queue
        self.processing_client.output_queue = self.process_queue
        self.inference_client.input_queue = self.process_queue
        self.inference_client.output_queue = self.inference_queue
        
        # Store callback
        self.callback = callback
        
        # Control flag
        self.should_run = True
        
        # Analysis thread
        self.analysis_thread = threading.Thread(target=self.process_analysis)
        
        logger.info("SystemClient initialized successfully")
    
    def process_analysis(self):
        """Process and display market analysis results."""
        logger.info("Starting analysis processing loop")
        
        while self.should_run:
            try:
                analysis = self.inference_queue.get(timeout=1.0)
                if analysis:
                    # Log the analysis with timestamp
                    logger.info(
                        f"\nSystem Status Update ({analysis.timestamp.strftime('%Y-%m-%d %H:%M:%S')}):"
                    )
                    logger.info("-" * 80)
                    logger.info(
                        f"Market Risk Score: {analysis.score:6.2f} | "
                        f"Current Regime: {analysis.regime.label}"
                    )
                    logger.info("-" * 80)
                    
                    # Call the callback if provided
                    if self.callback:
                        self.callback(analysis)
                        
            except queue.Empty:
                continue
            except Exception as e:
                logger.error(f"Error processing analysis: {str(e)}")
    
    def start(self):
        """Start all system components."""
        try:
            # Start fetch client
            self.fetch_client.start()
            logger.info("FetchClient started")
            
            # Start processing client
            self.processing_client.start()
            logger.info("ProcessingClient started")
            
            # Start inference client
            self.inference_client.start()
            logger.info("InferenceClient started")
            
            # Start analysis thread
            self.analysis_thread.start()
            logger.info("Analysis thread started")
            
            logger.info("System startup complete")
            
        except Exception as e:
            logger.error(f"System error: {str(e)}")
            self.stop()
            raise
    
    def stop(self):
        """Stop all system components."""
        logger.info("Initiating system shutdown")
        
        # Stop all clients
        self.should_run = False
        
        self.fetch_client.stop()
        self.processing_client.stop()
        self.inference_client.stop()
        
        # Stop analysis thread
        if self.analysis_thread.is_alive():
            self.analysis_thread.join()
        
        logger.info("System shutdown complete")

def example_callback(analysis):
    """Example callback function to demonstrate external system integration."""
    logger.info(
        f"External System Notification: "
        f"Market Risk Level = {analysis.score:.2f} ({analysis.regime.label})"
    )

def main():
    """Run the market analysis system."""
    try:
        # Create and start system
        system = SystemClient(callback=example_callback)
        system.start()
        
        # Keep main thread alive
        while True:
            try:
                input()  # Wait for Enter key
                break
            except KeyboardInterrupt:
                break
            
    except Exception as e:
        logger.error(f"System error: {str(e)}")
    finally:
        system.stop()

if __name__ == "__main__":
    main()
