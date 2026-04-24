import os
import json
import subprocess
from pathlib import Path
from typing import Optional
from agno.orchestrator.orchestrator import JobManifest
from agno.utils.log import log_info, log_error

class DockerRunner:
    """
    Executes a JobManifest inside an isolated Docker container.
    """
    def __init__(self, repo_root: Path):
        self.repo_root = repo_root
        self.image_name = "agno-sandbox"
        self.tmp_dir = self.repo_root / "tmp"
        self.outputs_dir = self.tmp_dir / "sandbox_outputs"
        
        # Ensure directories exist
        self.tmp_dir.mkdir(exist_ok=True)
        self.outputs_dir.mkdir(exist_ok=True)

    def _build_image(self):
        log_info(f"Ensuring Docker image '{self.image_name}' is built...")
        try:
            subprocess.run(
                ["docker", "build", "-t", self.image_name, "-f", "Dockerfile.sandbox", "."],
                cwd=str(self.repo_root),
                check=True,
                # capture_output=True # If we want to hide build logs
            )
        except subprocess.CalledProcessError as e:
            log_error(f"Failed to build Docker image: {e}")
            raise RuntimeError("Docker build failed.") from e
        except FileNotFoundError:
            raise RuntimeError("Docker is not installed or not running on this host.")

    def run(self, manifest: JobManifest) -> str:
        """
        Executes the manifest.
        Returns the path to the output directory.
        """
        self._build_image()
        
        manifest_path = self.tmp_dir / "sandbox_manifest.json"
        with open(manifest_path, 'w') as f:
            f.write(manifest.model_dump_json(indent=2))
            
        log_info("Starting Docker sandbox execution...")
        
        # Pass the API keys from the host environment to the container
        env_args = []
        for key in ["OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY"]:
            val = os.environ.get(key)
            if val:
                env_args.extend(["-e", f"{key}={val}"])
                
        docker_cmd = [
            "docker", "run", "--rm",
            "--add-host=host.docker.internal:host-gateway",
            # Mount the registry as read-only
            "-v", f"{self.repo_root / 'registry'}:/registry:ro",
            # Mount the manifest as read-only
            "-v", f"{manifest_path}:/app/manifest.json:ro",
            # Mount the output directory as read-write
            "-v", f"{self.outputs_dir}:/outputs:rw",
        ] + env_args + [
            self.image_name,
            "/app/manifest.json"
        ]
        
        try:
            result = subprocess.run(
                docker_cmd,
                cwd=str(self.repo_root),
                check=True,
                text=True,
            )
            log_info(f"Execution completed. Outputs saved to {self.outputs_dir}")
            return str(self.outputs_dir)
        except subprocess.CalledProcessError as e:
            log_error(f"Sandbox execution failed with exit code {e.returncode}")
            return str(self.outputs_dir)
