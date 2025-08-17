#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
LLMBench Runner - Benchmarking functionality for LLM services
"""

import time
import requests
import json
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass
import os
from savellmbench import LiveBenchmarkDisplay, create_live_display
from custom_prompts import CustomPromptsManager

@dataclass
class BenchmarkMetrics:
    """Container for benchmark timing metrics"""
    total_time: float  # Total time from submission to completion
    prompt_delay_time: float  # Time from submission to first token
    generation_time: float  # Time from first token to last token
    total_tokens: int  # Total tokens generated (including thinking if applicable)
    tokens_per_second: float  # Tokens/sec based on generation time only
    request_tokens_per_second: float  # Tokens/sec based on total request time
    prompt_name: str  # Which prompt was used
    service_name: str  # Which service was tested

class LLMBenchmarkRunner:
    """Handles the actual benchmarking of LLM services"""
    
    def __init__(self, service_info: Dict):
        self.service_info = service_info
        self.service_name = service_info['name']
        self.host = service_info['host']
        self.selected_model = service_info.get('selected_model', 'default')
        self.live_display = create_live_display(service_info)
        self.custom_prompts_manager = CustomPromptsManager()
        
        # Define canned prompts for testing
        self.canned_prompts = {
            "Prompt 1": "Write a 200 word story about a robot learning to paint.",
            "Prompt 2": "Explain the concept of quantum computing in 500 words or less.",
            "Prompt 3": "Create a recipe for a healthy breakfast that takes under 10 minutes to prepare.",
            "Prompt 4": "Write a Python function that calculates the fibonacci sequence up to n numbers.",
            "Prompt 5": "Describe what you would see on a walk through a forest in autumn."
        }
    
    def get_all_prompts(self) -> Dict[str, str]:
        """Get combined canned and custom prompts"""
        all_prompts = self.canned_prompts.copy()
        all_prompts.update(self.custom_prompts_manager.get_custom_prompts())
        return all_prompts
    
    def get_api_endpoint_and_payload(self, prompt: str, streaming: bool = True) -> Tuple[str, Dict]:
        """Get the appropriate API endpoint and payload for each service"""
        if self.service_name == "Ollama":
            endpoint = f"{self.host}/api/generate"
            payload = {
                "model": self.selected_model,
                "prompt": prompt,
                "stream": streaming
            }
        elif self.service_name == "vLLM":
            endpoint = f"{self.host}/v1/completions"
            payload = {
                "model": self.selected_model,
                "prompt": prompt,
                "max_tokens": 500,
                "stream": streaming
            }
        elif self.service_name == "Llama.cpp":
            endpoint = f"{self.host}/completion"
            payload = {
                "prompt": prompt,
                "n_predict": 500,
                "stream": streaming
            }
        else:
            raise ValueError(f"Unsupported service: {self.service_name}")
        
        return endpoint, payload
    
    def make_streaming_request(self, prompt: str, prompt_name: str) -> BenchmarkMetrics:
        """Make streaming API request with real-time updates"""
        endpoint, payload = self.get_api_endpoint_and_payload(prompt, streaming=True)
        
        # Get authentication headers if available
        headers = self.service_info.get('auth_headers', {'Content-Type': 'application/json'})
        
        # Start the live display for this prompt
        self.live_display.start_prompt_benchmark(prompt_name, prompt)
        
        # Record start time
        start_time = time.time()
        first_token_time = None
        accumulated_response = ""
        total_tokens = 0
        
        try:
            # Make streaming request
            response = requests.post(endpoint, json=payload, headers=headers, timeout=600, stream=True)
            response.raise_for_status()
            
            # Track last display update time for periodic refreshes
            last_display_update = time.time()
            
            # Process streaming response
            for line in response.iter_lines(decode_unicode=True):
                if line.strip():
                    try:
                        # Parse JSON line for streaming response
                        if self.service_name == "Ollama":
                            data = json.loads(line)
                            
                            # Mark first token time
                            if first_token_time is None:
                                first_token_time = time.time()
                                self.live_display.update_first_token()
                            
                            # Extract response chunk
                            chunk = data.get('response', '')
                            accumulated_response += chunk
                            
                            # Update live display with incremental content
                            if chunk:
                                # Estimate tokens (rough approximation)
                                estimated_tokens = int(len(accumulated_response.split()) * 1.3)
                                self.live_display.update_response(chunk, estimated_tokens)
                            
                            # Periodic display refresh for live timer (every 0.5 seconds)
                            current_time = time.time()
                            if current_time - last_display_update >= 0.5:
                                self.live_display._update_display()
                                last_display_update = current_time
                            
                            # Check if done
                            if data.get('done', False):
                                total_tokens = data.get('eval_count', estimated_tokens)
                                break
                                
                        elif self.service_name == "vLLM":
                            # vLLM streaming format
                            if line.startswith('data: '):
                                json_str = line[6:]  # Remove 'data: ' prefix
                                if json_str.strip() == '[DONE]':
                                    break
                                    
                                data = json.loads(json_str)
                                choices = data.get('choices', [])
                                if choices:
                                    # Mark first token time
                                    if first_token_time is None:
                                        first_token_time = time.time()
                                        self.live_display.update_first_token()
                                    
                                    chunk = choices[0].get('text', '')
                                    accumulated_response += chunk
                                    
                                    if chunk:
                                        estimated_tokens = int(len(accumulated_response.split()) * 1.3)
                                        self.live_display.update_response(chunk, estimated_tokens)
                                        
                                        # Periodic display refresh for live timer
                                        current_time = time.time()
                                        if current_time - last_display_update >= 0.5:
                                            self.live_display._update_display()
                                            last_display_update = current_time
                                        
                        elif self.service_name == "Llama.cpp":
                            # Llama.cpp streaming format
                            data = json.loads(line)
                            
                            # Mark first token time
                            if first_token_time is None:
                                first_token_time = time.time()
                                self.live_display.update_first_token()
                            
                            chunk = data.get('content', '')
                            accumulated_response += chunk
                            
                            if chunk:
                                estimated_tokens = int(len(accumulated_response.split()) * 1.3)
                                self.live_display.update_response(chunk, estimated_tokens)
                                
                                # Periodic display refresh for live timer
                                current_time = time.time()
                                if current_time - last_display_update >= 0.5:
                                    self.live_display._update_display()
                                    last_display_update = current_time
                            
                            # Check if generation is complete
                            if data.get('stop', False):
                                total_tokens = data.get('tokens_predicted', estimated_tokens)
                                break
                                
                    except json.JSONDecodeError:
                        # Skip malformed JSON lines
                        continue
                
                # Update display periodically even if no new content (for live timer)
                current_time = time.time()
                if current_time - last_display_update >= 1.0:  # Every 1 second when no new content
                    self.live_display._update_display()
                    last_display_update = current_time
            
            # Record completion time
            end_time = time.time()
            
            # Use first token time or start time if no tokens received
            if first_token_time is None:
                first_token_time = start_time
            
            # Final token count estimate if not provided
            if total_tokens == 0:
                total_tokens = int(len(accumulated_response.split()) * 1.3)
            
            # Update live display with final response
            self.live_display.complete_prompt_benchmark(accumulated_response, total_tokens)
            
            # Calculate metrics
            total_time = end_time - start_time
            prompt_delay_time = first_token_time - start_time
            generation_time = end_time - first_token_time
            
            # Avoid division by zero
            tokens_per_second = total_tokens / generation_time if generation_time > 0 else 0
            request_tokens_per_second = total_tokens / total_time if total_time > 0 else 0
            
            return BenchmarkMetrics(
                total_time=total_time,
                prompt_delay_time=prompt_delay_time,
                generation_time=generation_time,
                total_tokens=total_tokens,
                tokens_per_second=tokens_per_second,
                request_tokens_per_second=request_tokens_per_second,
                prompt_name=prompt_name,
                service_name=self.service_name
            )
            
        except requests.exceptions.RequestException as e:
            print(f"Streaming API request failed: {e}")
            raise
        except Exception as e:
            print(f"Error processing streaming response: {e}")
            raise
    
    def make_api_request_with_live_display(self, prompt: str, prompt_name: str) -> BenchmarkMetrics:
        """Make API request with live display updates (fallback to non-streaming)"""
        # Try streaming first
        try:
            return self.make_streaming_request(prompt, prompt_name)
        except Exception as e:
            print(f"Streaming failed ({e}), falling back to non-streaming...")
            time.sleep(1)  # Brief pause before fallback
            
        # Fallback to non-streaming
        endpoint, payload = self.get_api_endpoint_and_payload(prompt, streaming=False)
        
        # Get authentication headers if available
        headers = self.service_info.get('auth_headers', {'Content-Type': 'application/json'})
        
        # Start the live display for this prompt
        self.live_display.start_prompt_benchmark(prompt_name, prompt)
        
        # Record start time
        start_time = time.time()
        
        try:
            # Make the request with authentication headers
            response = requests.post(endpoint, json=payload, headers=headers, timeout=600)
            
            # Record when we get first response (approximates first token time)
            first_token_time = time.time()
            self.live_display.update_first_token()
            
            response.raise_for_status()
            result = response.json()
            
            # Record completion time
            end_time = time.time()
            
            # Extract response text and token count based on service
            response_text, total_tokens = self.extract_response_info(result)
            
            # Update live display with final response
            self.live_display.complete_prompt_benchmark(response_text, total_tokens)
            
            # Calculate metrics
            total_time = end_time - start_time
            prompt_delay_time = first_token_time - start_time
            generation_time = end_time - first_token_time
            
            # Avoid division by zero
            tokens_per_second = total_tokens / generation_time if generation_time > 0 else 0
            request_tokens_per_second = total_tokens / total_time if total_time > 0 else 0
            
            return BenchmarkMetrics(
                total_time=total_time,
                prompt_delay_time=prompt_delay_time,
                generation_time=generation_time,
                total_tokens=total_tokens,
                tokens_per_second=tokens_per_second,
                request_tokens_per_second=request_tokens_per_second,
                prompt_name=prompt_name,
                service_name=self.service_name
            )
            
        except requests.exceptions.RequestException as e:
            print(f"Non-streaming API request failed: {e}")
            raise
        except Exception as e:
            print(f"Error processing non-streaming response: {e}")
            raise
    
    def extract_response_info(self, result: Dict) -> Tuple[str, int]:
        """Extract response text and token count from API response"""
        if self.service_name == "Ollama":
            response_text = result.get('response', '')
            # Ollama doesn't always provide token count, estimate from text
            total_tokens = result.get('eval_count', len(response_text.split()) * 1.3)  # Rough estimate
            
        elif self.service_name == "vLLM":
            choices = result.get('choices', [])
            if choices:
                response_text = choices[0].get('text', '')
                usage = result.get('usage', {})
                total_tokens = usage.get('completion_tokens', len(response_text.split()) * 1.3)
            else:
                response_text = ''
                total_tokens = 0
                
        elif self.service_name == "Llama.cpp":
            response_text = result.get('content', '')
            # Llama.cpp might provide tokens_predicted
            total_tokens = result.get('tokens_predicted', len(response_text.split()) * 1.3)
        else:
            response_text = str(result)
            total_tokens = len(response_text.split()) * 1.3  # Fallback estimate
        
        return response_text, int(total_tokens)
    
    def run_single_benchmark(self, prompt_name: str, prompt_text: str) -> BenchmarkMetrics:
        """Run benchmark for a single prompt with live display"""
        try:
            metrics = self.make_api_request_with_live_display(prompt_text, prompt_name)
            
            # Wait a moment to show final results
            time.sleep(3)
            
            return metrics
        except Exception as e:
            print(f"Failed to run benchmark for {prompt_name}: {e}")
            return None
    
    def display_metrics(self, metrics: BenchmarkMetrics):
        """Display detailed metrics for a single benchmark run"""
        print(f"\n{'='*60}")
        print(f"BENCHMARK RESULTS: {metrics.prompt_name}")
        print(f"Service: {metrics.service_name}")
        print(f"{'='*60}")
        print(f"Total Request Time:     {metrics.total_time:.3f} seconds")
        print(f"Prompt Delay Time:      {metrics.prompt_delay_time:.3f} seconds")
        print(f"Generation Time:        {metrics.generation_time:.3f} seconds")
        print(f"Total Tokens Generated: {metrics.total_tokens}")
        print(f"Generation Speed:       {metrics.tokens_per_second:.2f} tokens/sec")
        print(f"Overall Request Speed:  {metrics.request_tokens_per_second:.2f} tokens/sec")
        print(f"{'='*60}")
    
    def display_summary(self, all_metrics: List[BenchmarkMetrics]):
        """Display summary statistics across all benchmark runs"""
        if not all_metrics:
            print("No successful benchmark runs to summarize.")
            return
        
        print(f"\n{'='*80}")
        print(f"BENCHMARK SUMMARY - {self.service_name}")
        print(f"{'='*80}")
        
        # Calculate averages
        avg_total_time = sum(m.total_time for m in all_metrics) / len(all_metrics)
        avg_prompt_delay = sum(m.prompt_delay_time for m in all_metrics) / len(all_metrics)
        avg_generation_time = sum(m.generation_time for m in all_metrics) / len(all_metrics)
        avg_tokens = sum(m.total_tokens for m in all_metrics) / len(all_metrics)
        avg_gen_speed = sum(m.tokens_per_second for m in all_metrics) / len(all_metrics)
        avg_req_speed = sum(m.request_tokens_per_second for m in all_metrics) / len(all_metrics)
        
        print(f"Prompts Tested:           {len(all_metrics)}")
        print(f"Average Total Time:       {avg_total_time:.3f} seconds")
        print(f"Average Prompt Delay:     {avg_prompt_delay:.3f} seconds")
        print(f"Average Generation Time:  {avg_generation_time:.3f} seconds")
        print(f"Average Tokens Generated: {avg_tokens:.1f}")
        print(f"Average Generation Speed: {avg_gen_speed:.2f} tokens/sec")
        print(f"Average Request Speed:    {avg_req_speed:.2f} tokens/sec")
        print(f"{'='*80}")

def prompt_selection_menu(runner: LLMBenchmarkRunner) -> List[str]:
    """Display menu for prompt selection and return selected prompt names"""
    
    while True:
        # Get current prompts (includes both canned and custom)
        all_prompts = runner.get_all_prompts()
        
        print(f"\n{'='*60}")
        print("SELECT PROMPTS TO BENCHMARK")
        print(f"{'='*60}")
        
        # Display available prompts
        prompt_list = list(all_prompts.keys())
        for i, prompt_name in enumerate(prompt_list, 1):
            print(f"{i}. {prompt_name}")
            prompt_text = all_prompts[prompt_name]
            preview = prompt_text[:50] + ('...' if len(prompt_text) > 50 else '')
            print(f"   \"{preview}\"")
            print()
        
        print(f"{len(prompt_list) + 1}. Run ALL prompts")
        print("0. Add custom prompt")
        print("99. Return to main menu")
        
        try:
            choice = input(f"\nEnter your choice (0, 1-{len(prompt_list) + 1}, 99): ").strip()
            
            if choice == '99':
                return []
            elif choice == '0':
                # Add custom prompt
                custom_prompt_text = runner.custom_prompts_manager.get_prompt_input()
                if custom_prompt_text:
                    prompt_name = runner.custom_prompts_manager.add_custom_prompt(custom_prompt_text)
                    print(f"\n✓ Custom prompt added as '{prompt_name}'")
                    print("You can now select it from the updated menu.")
                # Continue to show menu again with new prompt
                continue
            elif choice == str(len(prompt_list) + 1):
                return prompt_list
            else:
                choice_num = int(choice)
                if 1 <= choice_num <= len(prompt_list):
                    return [prompt_list[choice_num - 1]]
                else:
                    print(f"Please enter a valid number (0, 1-{len(prompt_list) + 1}, or 99)")
        except ValueError:
            print("Please enter a valid number")
        except KeyboardInterrupt:
            print("\nReturning to main menu...")
            return []

def run_benchmark(service_info: Dict):
    """Main benchmark runner function called from llmbench.py"""
    runner = LLMBenchmarkRunner(service_info)
    
    # Check if service is actually responding to API calls
    if not service_info.get('api_responding', False):
        print(f"\nWarning: {service_info['name']} API is not responding.")
        print("The benchmark may fail. Please ensure the service is running and accessible.")
        
        choice = input("Continue anyway? (y/n): ").strip().lower()
        if choice != 'y':
            print("Benchmark cancelled.")
            return
    
    # Show prompt selection menu
    selected_prompts = prompt_selection_menu(runner)
    
    if not selected_prompts:
        print("No prompts selected. Returning to main menu.")
        return
    
    print(f"\nStarting benchmark with {len(selected_prompts)} prompt(s)...")
    print(f"Service: {service_info['name']} at {service_info['host']}")
    print(f"Model: {service_info.get('selected_model', 'default')}")
    
    # Start the live display session
    runner.live_display.start_session()
    
    try:
        # Run benchmarks
        all_metrics = []
        all_prompts = runner.get_all_prompts()
        for prompt_name in selected_prompts:
            prompt_text = all_prompts[prompt_name]
            metrics = runner.run_single_benchmark(prompt_name, prompt_text)
            
            if metrics:
                all_metrics.append(metrics)
            
            # Small delay between requests to be nice to the API
            if len(selected_prompts) > 1:
                time.sleep(2)
        
        # End the live display session
        runner.live_display.end_session()
        
        # Display summary if multiple prompts were run
        if len(all_metrics) > 1:
            print("\n")  # Add some space after live display
            runner.display_summary(all_metrics)
        
        print(f"\nBenchmark complete! {len(all_metrics)} successful runs out of {len(selected_prompts)} attempted.")
        
    except KeyboardInterrupt:
        print("\nBenchmark interrupted by user.")
        runner.live_display.end_session()
    except Exception as e:
        print(f"\nBenchmark failed: {e}")
        runner.live_display.end_session()

if __name__ == "__main__":
    # For testing purposes
    test_service = {
        'name': 'Test Service',
        'host': 'http://localhost:8080',
        'api_responding': False
    }
    run_benchmark(test_service)