#!/usr/bin/env python3
"""
Custom Prompts Manager - Handles user-defined prompts with persistent storage
"""

import json
import os
from typing import Dict, Optional
from pathlib import Path

class CustomPromptsManager:
    """Manages custom user prompts with persistent storage"""
    
    def __init__(self):
        self.prompts_file = "custom_prompts.json"
        self.custom_prompts: Dict[str, str] = {}
        self.load_custom_prompts()
    
    def load_custom_prompts(self):
        """Load custom prompts from file"""
        try:
            if os.path.exists(self.prompts_file):
                with open(self.prompts_file, 'r', encoding='utf-8') as f:
                    self.custom_prompts = json.load(f)
                print(f"✓ Loaded {len(self.custom_prompts)} custom prompts")
            else:
                self.custom_prompts = {}
        except Exception as e:
            print(f"Warning: Could not load custom prompts: {e}")
            self.custom_prompts = {}
    
    def save_custom_prompts(self):
        """Save custom prompts to file"""
        try:
            with open(self.prompts_file, 'w', encoding='utf-8') as f:
                json.dump(self.custom_prompts, f, indent=2, ensure_ascii=False)
            print(f"✓ Saved {len(self.custom_prompts)} custom prompts")
        except Exception as e:
            print(f"Warning: Could not save custom prompts: {e}")
    
    def add_custom_prompt(self, prompt_text: str) -> str:
        """Add a new custom prompt and return its assigned name"""
        # Generate a name based on the number of existing custom prompts
        prompt_count = len(self.custom_prompts) + 1
        prompt_name = f"Custom {prompt_count}"
        
        # Ensure unique name
        while prompt_name in self.custom_prompts:
            prompt_count += 1
            prompt_name = f"Custom {prompt_count}"
        
        # Add the prompt
        self.custom_prompts[prompt_name] = prompt_text
        self.save_custom_prompts()
        
        return prompt_name
    
    def get_custom_prompts(self) -> Dict[str, str]:
        """Get all custom prompts"""
        return self.custom_prompts.copy()
    
    def delete_custom_prompt(self, prompt_name: str) -> bool:
        """Delete a custom prompt"""
        if prompt_name in self.custom_prompts:
            del self.custom_prompts[prompt_name]
            self.save_custom_prompts()
            return True
        return False
    
    def get_prompt_input(self) -> Optional[str]:
        """Get custom prompt input from user with validation"""
        print(f"\n{'='*60}")
        print("ADD CUSTOM PROMPT")
        print(f"{'='*60}")
        print("Enter your custom prompt below. Press Enter twice when finished.")
        print("Type 'cancel' to return to the menu.")
        print("-" * 60)
        
        lines = []
        empty_line_count = 0
        
        while True:
            try:
                line = input()
                
                # Check for cancel
                if line.strip().lower() == 'cancel':
                    print("Custom prompt cancelled.")
                    return None
                
                # Track empty lines for completion detection
                if line.strip() == "":
                    empty_line_count += 1
                    if empty_line_count >= 2:
                        break
                else:
                    empty_line_count = 0
                
                lines.append(line)
                
            except KeyboardInterrupt:
                print("\nCustom prompt cancelled.")
                return None
        
        # Join lines and clean up
        prompt_text = "\n".join(lines).strip()
        
        if not prompt_text:
            print("Empty prompt not saved.")
            return None
        
        # Confirm the prompt
        print(f"\n{'='*60}")
        print("PROMPT PREVIEW:")
        print(f"{'='*60}")
        print(prompt_text)
        print(f"{'='*60}")
        
        while True:
            try:
                confirm = input("\nSave this prompt? (y/n): ").strip().lower()
                if confirm in ['y', 'yes']:
                    return prompt_text
                elif confirm in ['n', 'no']:
                    print("Prompt not saved.")
                    return None
                else:
                    print("Please enter 'y' or 'n'")
            except KeyboardInterrupt:
                print("\nPrompt not saved.")
                return None