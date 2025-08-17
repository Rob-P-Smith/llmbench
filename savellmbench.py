#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLMBench Save Module - Real-time display and file output for benchmark results
"""

import os
import time
import threading
from datetime import datetime
from typing import Dict, Optional, TextIO
from dataclasses import dataclass
import sys

@dataclass
class LiveMetrics:
    """Container for live benchmark metrics"""
    start_time: float
    first_token_time: Optional[float] = None
    current_time: float = 0.0
    total_tokens: int = 0
    response_text: str = ""
    prompt_name: str = ""
    service_name: str = ""
    model_name: str = ""
    
    @property
    def total_elapsed(self) -> float:
        """Total time elapsed since start"""
        return self.current_time - self.start_time if self.current_time > self.start_time else 0.0
    
    @property
    def prompt_delay_time(self) -> float:
        """Time from start to first token"""
        return self.first_token_time - self.start_time if self.first_token_time else 0.0
    
    @property
    def generation_time(self) -> float:
        """Time from first token to current time"""
        if self.first_token_time and self.current_time > self.first_token_time:
            return self.current_time - self.first_token_time
        return 0.0
    
    @property
    def tokens_per_second(self) -> float:
        """Tokens per second based on generation time"""
        if self.generation_time > 0 and self.total_tokens > 0:
            return self.total_tokens / self.generation_time
        return 0.0
    
    @property
    def request_tokens_per_second(self) -> float:
        """Tokens per second based on total elapsed time"""
        if self.total_elapsed > 0 and self.total_tokens > 0:
            return self.total_tokens / self.total_elapsed
        return 0.0

class LiveBenchmarkDisplay:
    """Handles real-time display and file output for benchmark results"""
    
    def __init__(self, service_info: Dict):
        self.service_info = service_info
        self.service_name = service_info['name']
        self.model_name = service_info.get('selected_model', 'default')
        
        # Create results directory if it doesn't exist
        self.results_dir = "results"
        if not os.path.exists(self.results_dir):
            os.makedirs(self.results_dir)
        
        # Create output filename with timestamp
        self.start_datetime = datetime.now()
        timestamp = self.start_datetime.strftime("%Y%m%d_%H%M%S")
        self.output_filename = os.path.join(self.results_dir, f"benchmark_output_{timestamp}.txt")
        
        # Live metrics tracking
        self.current_metrics: Optional[LiveMetrics] = None
        self.output_file: Optional[TextIO] = None
        self.display_lock = threading.Lock()
        self.running = False
        
    def start_session(self):
        """Start a new benchmark session"""
        self.running = True
        try:
            self.output_file = open(self.output_filename, 'w', encoding='utf-8')
            self._write_session_header()
            print(f"\\nBenchmark session started. Results will be saved to: {self.output_filename}")
        except Exception as e:
            print(f"Error creating output file: {e}")
            self.output_file = None
    
    def end_session(self):
        """End the benchmark session"""
        self.running = False
        if self.output_file:
            self._write_session_footer()
            self.output_file.close()
            print(f"\\nBenchmark session complete. Results saved to: {self.output_filename}")
    
    def _write_session_header(self):
        """Write session header to file"""
        if not self.output_file:
            return
            
        header = f"""{'='*80}
LLMBench Results - {self.start_datetime.strftime('%Y-%m-%d %H:%M:%S')}
{'='*80}
Service: {self.service_name}
Model: {self.model_name}
Host: {self.service_info['host']}
{'='*80}

"""
        self.output_file.write(header)
        self.output_file.flush()
    
    def _write_session_footer(self):
        """Write session footer to file"""
        if not self.output_file:
            return
            
        end_time = datetime.now()
        footer = f"""

{'='*80}
Session completed: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
Total session duration: {(end_time - self.start_datetime).total_seconds():.2f} seconds
{'='*80}
"""
        self.output_file.write(footer)
        self.output_file.flush()
    
    def start_prompt_benchmark(self, prompt_name: str, prompt_text: str):
        """Start benchmarking a new prompt"""
        with self.display_lock:
            self.current_metrics = LiveMetrics(
                start_time=time.time(),
                prompt_name=prompt_name,
                service_name=self.service_name,
                model_name=self.model_name
            )
            
            # Write prompt info to file
            if self.output_file:
                prompt_header = f"""
{'='*60}
PROMPT: {prompt_name}
{'='*60}
Prompt Text: {prompt_text}
Started: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

"""
                self.output_file.write(prompt_header)
                self.output_file.flush()
        
        self._update_display()
    
    def update_first_token(self):
        """Mark the time when first token is received"""
        if self.current_metrics:
            with self.display_lock:
                self.current_metrics.first_token_time = time.time()
            self._update_display()
    
    def update_response(self, additional_text: str, token_count: int = None):
        """Update the response text and token count"""
        if self.current_metrics:
            with self.display_lock:
                self.current_metrics.response_text += additional_text
                self.current_metrics.current_time = time.time()
                if token_count is not None:
                    self.current_metrics.total_tokens = token_count
                else:
                    # Rough estimate if no token count provided
                    estimated_tokens = len(self.current_metrics.response_text.split()) * 1.3
                    self.current_metrics.total_tokens = int(estimated_tokens)
            self._update_display()
    
    def complete_prompt_benchmark(self, final_response: str, final_token_count: int):
        """Complete the current prompt benchmark"""
        if self.current_metrics:
            with self.display_lock:
                self.current_metrics.response_text = final_response
                self.current_metrics.total_tokens = final_token_count
                self.current_metrics.current_time = time.time()
            
            self._update_display()
            self._write_final_results()
    
    def _update_display(self):
        """Update the live display"""
        if not self.current_metrics:
            return
        
        # Clear screen (works on most terminals)
        os.system('cls' if os.name == 'nt' else 'clear')
        
        metrics = self.current_metrics
        
        # Display header
        print(f"{'='*80}")
        print(f"LIVE BENCHMARK - {metrics.prompt_name}")
        print(f"Service: {metrics.service_name} | Model: {metrics.model_name}")
        print(f"{'='*80}")
        
        # Display metrics
        print(f"\\nMETRICS:")
        print(f"Total Elapsed Time:     {metrics.total_elapsed:.3f} seconds")
        
        if metrics.first_token_time:
            print(f"Prompt Delay Time:      {metrics.prompt_delay_time:.3f} seconds")
            print(f"Generation Time:        {metrics.generation_time:.3f} seconds")
        else:
            print(f"Prompt Delay Time:      [Waiting for first token...]")
            print(f"Generation Time:        [Waiting for first token...]")
        
        print(f"Total Tokens Generated: {metrics.total_tokens}")
        
        if metrics.tokens_per_second > 0:
            print(f"Generation Speed:       {metrics.tokens_per_second:.2f} tokens/sec")
        else:
            print(f"Generation Speed:       [Calculating...]")
            
        if metrics.request_tokens_per_second > 0:
            print(f"Overall Request Speed:  {metrics.request_tokens_per_second:.2f} tokens/sec")
        else:
            print(f"Overall Request Speed:  [Calculating...]")
        
        # Display response
        print(f"\\n{'='*80}")
        print(f"RESPONSE:")
        print(f"{'='*80}")
        
        if metrics.response_text:
            # Truncate response for display if too long
            display_response = metrics.response_text
            if len(display_response) > 2000:
                display_response = display_response[:2000] + "\\n[... truncated for display ...]"
            print(display_response)
        else:
            print("[Waiting for response...]")
        
        print(f"\\n{'='*80}")
        
        # Force flush to ensure immediate display
        sys.stdout.flush()
    
    def _write_final_results(self):
        """Write final results to file"""
        if not self.output_file or not self.current_metrics:
            return
        
        metrics = self.current_metrics
        
        results = f"""METRICS:
total_elapsed_time: {metrics.total_elapsed:.3f}
prompt_delay_time: {metrics.prompt_delay_time:.3f}
generation_time: {metrics.generation_time:.3f}
total_tokens_generated: {metrics.total_tokens}
generation_speed_tokens_per_sec: {metrics.tokens_per_second:.2f}
overall_request_speed_tokens_per_sec: {metrics.request_tokens_per_second:.2f}
completed_at: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

RESPONSE:
{metrics.response_text}

{'='*60}

"""
        
        self.output_file.write(results)
        self.output_file.flush()

def create_live_display(service_info: Dict) -> LiveBenchmarkDisplay:
    """Factory function to create a live display instance"""
    return LiveBenchmarkDisplay(service_info)

# Example usage for testing
if __name__ == "__main__":
    # Test the live display functionality
    test_service = {
        'name': 'Test Service',
        'host': 'http://localhost:8080',
        'selected_model': 'test_model'
    }
    
    display = create_live_display(test_service)
    display.start_session()
    
    # Simulate a benchmark
    display.start_prompt_benchmark("Test Prompt", "This is a test prompt for the display system.")
    
    time.sleep(1)
    display.update_first_token()
    
    # Simulate streaming response
    response_parts = [
        "This is the beginning of the response. ",
        "The model is generating text progressively. ",
        "Each update shows more of the response. ",
        "The metrics are calculated in real-time. ",
        "This demonstrates the live updating functionality."
    ]
    
    for i, part in enumerate(response_parts):
        time.sleep(0.5)
        display.update_response(part, (i + 1) * 10)
    
    # Complete the benchmark
    full_response = "".join(response_parts)
    display.complete_prompt_benchmark(full_response, 50)
    
    time.sleep(2)
    display.end_session()
    
    print("\\nTest completed. Check the generated benchmark_output_*.txt file.")