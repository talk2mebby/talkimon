import click
import subprocess
import os

@click.group()
def cli():
    pass

@cli.command()
def start():
    print("[MeshNode CLI] Starting MeshNode...")
    subprocess.call(["python3", "meshnode/main.py"])

@cli.command()
def status():
    print("[MeshNode CLI] Status check (TBD)")

@cli.command()
def reload():
    print("[MeshNode CLI] Sending reload request...")
    os.system("curl -X POST http://localhost:8000/reload-devices -H 'x-api-key: my-secret-api-key'")

@cli.command()
def logs():
    os.system("tail -f logs/meshnode.log")

if __name__ == "__main__":
    cli()
