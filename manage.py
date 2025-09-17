#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import subprocess

subprocess.run(["python", "-m", "pip", "install", "--upgrade", "pip"])
requirements_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'requirements.txt')
print("Verifying install of requirements")
if os.path.exists(requirements_file):
    try:
        subprocess.run(['pip','install','--upgrade','-r',requirements_file, '-q' ] , check=True) #Remove -q to see output of installs
    except subprocess.CalledProcessError as e:
        print(f"Failed to install requirements: {e}, stopping launch.")
        sys.exit(1)
def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'djangoBackend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
