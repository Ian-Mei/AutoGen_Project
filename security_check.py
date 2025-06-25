#!/usr/bin/env python3
"""
Security check script for Google Sheets API credentials
Run this to verify your credentials are properly secured
"""

import os
import stat
import subprocess

# Constants for sensitive files
CREDENTIALS_FILE = "credentials.json"
TOKEN_FILE = "token.json"
ENV_FILE = ".env"
SENSITIVE_FILES = [CREDENTIALS_FILE, TOKEN_FILE, ENV_FILE]


def check_git_status():
    """Check if sensitive files are tracked by git"""
    print("🔍 Checking Git Status...")

    issues = []

    try:
        # Check if we're in a git repo and get tracked files
        tracked_result = subprocess.run(
            ["git", "ls-files"], capture_output=True, text=True, check=True
        )
        tracked_files = tracked_result.stdout.strip().split("\n")

        for file in SENSITIVE_FILES:
            if file in tracked_files:
                issues.append(f"❌ {file} is tracked by Git!")
            elif os.path.exists(file):
                print(f"✅ {file} exists and is not tracked by Git")

    except subprocess.CalledProcessError:
        print("⚠️ Not in a Git repository or Git not available")
        return issues

    return issues


def check_file_permissions():
    """Check file permissions for sensitive files"""
    print("\n🔒 Checking File Permissions...")

    sensitive_files = [
        (CREDENTIALS_FILE, "Google Sheets credentials"),
        (TOKEN_FILE, "Google Sheets access token"),
        (ENV_FILE, "Environment variables"),
    ]

    issues = []

    for filename, description in sensitive_files:
        if os.path.exists(filename):
            if os.name != "nt":  # Unix-like systems
                file_stat = os.stat(filename)
                permissions = oct(file_stat.st_mode)[-3:]

                if permissions == "600":
                    print(f"✅ {filename} has secure permissions (600)")
                else:
                    print(f"⚠️ {filename} has permissions {permissions} - should be 600")
                    issues.append(f"Run: chmod 600 {filename}")
            else:  # Windows
                print(f"ℹ️ {filename} found (Windows permissions not checked)")
        else:
            print(f"ℹ️ {filename} not found")

    return issues


def check_gitignore():
    """Check if .gitignore properly excludes sensitive files"""
    print("\n📝 Checking .gitignore...")

    required_entries = [CREDENTIALS_FILE, TOKEN_FILE, ENV_FILE]
    issues = []

    if os.path.exists(".gitignore"):
        with open(".gitignore", "r") as f:
            gitignore_content = f.read()

        for entry in required_entries:
            if entry in gitignore_content:
                print(f"✅ {entry} is in .gitignore")
            else:
                print(f"❌ {entry} is NOT in .gitignore")
                issues.append(f"Add {entry} to .gitignore")
    else:
        print("❌ .gitignore file not found")
        issues.append("Create .gitignore file")

    return issues


def check_environment():
    """Check environment setup"""
    print("\n🌍 Checking Environment...")

    issues = []

    # Check if running in virtual environment
    if hasattr(sys, "real_prefix") or (
        hasattr(sys, "base_prefix") and sys.base_prefix != sys.prefix
    ):
        print("✅ Running in virtual environment")
    else:
        print("⚠️ Not running in virtual environment")
        issues.append("Consider using a virtual environment")

    # Check if .env is being used
    if os.path.exists(".env"):
        print("✅ .env file found")
        with open(".env", "r") as f:
            env_content = f.read()

        if "OPENAI_API_KEY" in env_content:
            print("✅ OpenAI API key configured")
        else:
            print("⚠️ OpenAI API key not found in .env")
    else:
        print("⚠️ .env file not found")

    return issues


def run_security_audit():
    """Run complete security audit"""
    print("🔐 Google Sheets API Security Audit")
    print("=" * 50)

    all_issues = []

    # Run all checks
    all_issues.extend(check_git_status())
    all_issues.extend(check_file_permissions())
    all_issues.extend(check_gitignore())
    all_issues.extend(check_environment())

    # Summary
    print("\n📊 Security Audit Summary")
    print("=" * 50)

    if not all_issues:
        print("🎉 All security checks passed!")
        print("✅ Your credentials appear to be properly secured")
    else:
        print(f"⚠️ Found {len(all_issues)} security issues to address:")
        for i, issue in enumerate(all_issues, 1):
            print(f"   {i}. {issue}")

        print("\n🔧 Quick fixes:")
        print("   - Run: chmod 600 credentials.json token.json .env")
        print("   - Ensure .gitignore includes sensitive files")
        print("   - Never commit credentials to version control")
        print("   - See SECURITY.md for detailed guidelines")

    return len(all_issues) == 0


if __name__ == "__main__":
    import sys

    success = run_security_audit()

    if success:
        print("\n✅ Security audit passed!")
        sys.exit(0)
    else:
        print("\n❌ Security issues found. Please address them before proceeding.")
        sys.exit(1)
