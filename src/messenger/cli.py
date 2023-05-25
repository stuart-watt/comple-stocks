"""Creates the CLI command to execute the messenger service"""
import fire

from main import main

if __name__ == "__main__":
    fire.Fire(main)
