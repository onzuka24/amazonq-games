#!/usr/bin/env python3
"""
AWS Services Anagram Game

A simple game where players unscramble anagrams of AWS service names.
"""

import random
import time
import sys

# List of AWS services for the anagram game
AWS_SERVICES = [
    "Lambda", "S3", "EC2", "DynamoDB", "CloudFront", "SageMaker", 
    "Redshift", "RDS", "SNS", "SQS", "Cognito", "Athena", 
    "Glue", "Kinesis", "CloudWatch", "IAM", "Route53", "ECS",
    "Fargate", "EKS", "Amplify", "AppSync", "Aurora", "Batch",
    "CodeBuild", "CodePipeline", "Comprehend", "Connect", "EFS"
]

def create_anagram(word):
    """Create an anagram by shuffling the letters of a word."""
    if len(word) <= 1:
        return word
    
    word_chars = list(word)
    random.shuffle(word_chars)
    
    # Make sure the anagram is different from the original word
    anagram = ''.join(word_chars)
    while anagram == word and len(word) > 1:
        random.shuffle(word_chars)
        anagram = ''.join(word_chars)
    
    return anagram

def play_game():
    """Main game function."""
    score = 0
    total_questions = 0
    
    print("\n===== AWS SERVICES ANAGRAM GAME =====")
    print("Unscramble the AWS service names. Type 'quit' to exit.")
    print("======================================\n")
    
    # Shuffle the services list
    services = AWS_SERVICES.copy()
    random.shuffle(services)
    
    for service in services:
        anagram = create_anagram(service)
        total_questions += 1
        
        print(f"\nAnagram #{total_questions}: {anagram}")
        start_time = time.time()
        
        guess = input("Your answer: ").strip()
        
        if guess.lower() == 'quit':
            break
        
        elapsed_time = time.time() - start_time
        
        if guess.lower() == service.lower():
            points = max(1, int(10 - elapsed_time/2)) if elapsed_time < 20 else 1
            score += points
            print(f"✓ Correct! +{points} points (answered in {elapsed_time:.1f} seconds)")
        else:
            print(f"✗ Wrong! The correct answer was: {service}")
        
        print(f"Current score: {score}")
        
        # Ask if the player wants to continue after every 5 questions
        if total_questions % 5 == 0 and total_questions < len(services):
            continue_game = input("\nContinue playing? (y/n): ").strip().lower()
            if continue_game != 'y':
                break
    
    print(f"\n===== GAME OVER =====")
    print(f"Final score: {score} out of a possible {total_questions * 10}")
    print(f"AWS services attempted: {total_questions} out of {len(AWS_SERVICES)}")
    
    if score > 0:
        accuracy = (score / (total_questions * 10)) * 100
        print(f"Performance: {accuracy:.1f}%")
    
    print("=====================")

if __name__ == "__main__":
    # Set random seed for reproducibility in testing
    random.seed(time.time())
    
    try:
        play_game()
    except KeyboardInterrupt:
        print("\n\nGame interrupted. Thanks for playing!")
        sys.exit(0)
