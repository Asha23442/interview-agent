"""
Verification Script for AI Interview Agent

Tests if core modules import correctly, checks directory permissions,
verifies environment configuration, and ensures fallback question generation works.
This script uses standard ASCII output to ensure compatibility across all command lines (Windows/Unix).
"""

import os
import sys

def run_tests():
    print("=" * 60)
    print("RUNNING INTERVIEW AGENT SYSTEM VERIFICATION")
    print("=" * 60)

    # 1. Test Imports
    print("\n1. Verifying module imports...")
    try:
        import streamlit as st
        import dotenv
        import groq
        print(" -> Third-party libraries imported successfully.")
    except ImportError as e:
        print(f" -> Third-party library import failed: {str(e)}")
        print("Please run: pip install -r requirements.txt")
        sys.exit(1)

    try:
        import prompt
        import utils
        import scorer
        import interview
        print(" -> Custom project modules imported successfully.")
    except ImportError as e:
        print(f" -> Custom module import failed: {str(e)}")
        sys.exit(1)

    # 2. Test Directory Initialization
    print("\n2. Verifying directory management...")
    try:
        utils.initialize_directories()
        assert os.path.exists("outputs"), "outputs directory missing"
        assert os.path.exists("data"), "data directory missing"
        print(" -> Application directories initialized successfully.")
    except Exception as e:
        print(f" -> Directory initialization failed: {str(e)}")
        sys.exit(1)

    # 3. Test Configuration & API Key Environment
    print("\n3. Verifying environmental configuration...")
    env_exists = os.path.exists(".env")
    if env_exists:
        print(" -> Found '.env' file.")
        api_key = os.getenv("GROQ_API_KEY")
        if api_key:
            # Mask the API key for display
            masked = api_key[:6] + "..." + api_key[-4:] if len(api_key) > 10 else "invalid"
            print(f" -> GROQ_API_KEY is configured: {masked}")
            print(f" -> Target model configured: {os.getenv('GROQ_MODEL', utils.DEFAULT_MODEL)}")
        else:
            print(" -> GROQ_API_KEY is not set in '.env'. The app will run in fallback question mode.")
    else:
        print(" -> '.env' file not found. The app will run in fallback question mode until configured.")

    # 4. Test Fallback Question Engine
    print("\n4. Verifying question generator fallback robustness...")
    try:
        # Generate questions for a custom role where we don't have hardcoded fallbacks
        test_role = "Quantum Software Engineer"
        questions = interview.generate_questions(test_role, "Experienced")
        
        assert len(questions) == 5, f"Expected 5 questions, got {len(questions)}"
        print(f" -> Successfully generated exactly {len(questions)} questions for '{test_role}'.")
        print("   Sample generated question:")
        print(f"   -> '{questions[0]}'")
    except Exception as e:
        print(f" -> Question generation engine crashed: {str(e)}")
        sys.exit(1)

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! Your Interview Agent is ready to run.")
    print("Run command: streamlit run app.py")
    print("=" * 60)

if __name__ == "__main__":
    run_tests()
