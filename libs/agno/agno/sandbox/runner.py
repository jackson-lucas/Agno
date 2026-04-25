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
        self.workspace_dir = self.outputs_dir / "workspace"
        
        # Ensure directories exist
        self.tmp_dir.mkdir(exist_ok=True)
        self.outputs_dir.mkdir(exist_ok=True)
        self.workspace_dir.mkdir(exist_ok=True)

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

    def run(self, manifest: JobManifest, log_callback: Optional[callable] = None) -> str:
        """
        Executes the manifest.
        Returns the path to the output directory.
        """
        self._build_image()
        
        manifest_path = self.tmp_dir / "sandbox_manifest.json"
        with open(manifest_path, 'w') as f:
            f.write(manifest.model_dump_json(indent=2))
            
        log_msg = "Starting Docker sandbox execution..."
        log_info(log_msg)
        if log_callback:
            log_callback(log_msg)
        
        # Pass the API keys and Git credentials from the host environment to the container
        # Try to load from .env if not in environment
        try:
            from dotenv import load_dotenv
            load_dotenv(dotenv_path=self.repo_root / ".env")
        except ImportError:
            pass

        env_args = []
        for key in ["OPENAI_API_KEY", "GEMINI_API_KEY", "GOOGLE_API_KEY", "GITHUB_TOKEN"]:
            val = os.environ.get(key)
            if val:
                env_args.extend(["-e", f"{key}={val}"])
                
        # Handle Repository Ingestion
        repo_mount_args = []
        if manifest.repo_url:
            log_info(f"Cloning remote repository: {manifest.repo_url}")
            try:
                # Clear workspace before cloning
                if self.workspace_dir.exists():
                    import shutil
                    shutil.rmtree(self.workspace_dir)
                self.workspace_dir.mkdir(exist_ok=True)
                
                subprocess.run(
                    ["git", "clone", manifest.repo_url, "."],
                    cwd=str(self.workspace_dir),
                    check=True,
                    capture_output=True
                )
            except subprocess.CalledProcessError as e:
                log_error(f"Failed to clone repository: {e.stderr.decode()}")
                raise RuntimeError(f"Git clone failed: {e.stderr.decode()}")
        elif manifest.repo_path:
            # Mount local path
            local_path = Path(manifest.repo_path).resolve()
            if not local_path.exists():
                raise RuntimeError(f"Local repo path does not exist: {local_path}")
            log_info(f"Using local repository: {local_path}")
            repo_mount_args = ["-v", f"{local_path}:/app/workspace:rw"]
        else:
            # If no repo provided, just mount the empty workspace_dir
            repo_mount_args = ["-v", f"{self.workspace_dir}:/app/workspace:rw"]

        docker_cmd = [
            "docker", "run", "--rm",
            "--add-host=host.docker.internal:host-gateway",
            # Mount the registry as read-only
            "-v", f"{self.repo_root / 'registry'}:/registry:ro",
            # Mount the manifest as read-only
            "-v", f"{manifest_path}:/app/manifest.json:ro",
            # Mount the output directory
            "-v", f"{self.outputs_dir}:/outputs:rw",
        ] + repo_mount_args + env_args + [
            self.image_name,
            "/app/manifest.json"
        ]
        
        try:
            # Use Popen to stream logs
            process = subprocess.Popen(
                docker_cmd,
                cwd=str(self.repo_root),
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                bufsize=1,
                universal_newlines=True,
            )
            
            if process.stdout:
                for line in process.stdout:
                    clean_line = line.strip()
                    if clean_line:
                        print(clean_line) # Print to host console
                        if log_callback:
                            log_callback(clean_line)
            
            process.wait()
            if process.returncode == 0:
                log_info(f"Execution completed. Outputs saved to {self.outputs_dir}")
            else:
                log_error(f"Sandbox execution failed with exit code {process.returncode}")
            return str(self.outputs_dir)
        except Exception as e:
            log_error(f"Error during sandbox execution: {e}")
            return str(self.outputs_dir)
