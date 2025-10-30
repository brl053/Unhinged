#!/usr/bin/env python3
"""
Generate protobuf files for speech-to-text service
"""
import subprocess
import sys
from pathlib import Path

from events import create_service_logger

# Initialize event logger
events = create_service_logger("proto-generator", "1.0.0")

def generate_proto_files():
    """Generate protobuf files from proto definitions"""

    # Find proto files
    proto_dir = Path("/app/proto")
    if not proto_dir.exists():
        # Proto directory not found
        return False

    # Output directory
    output_dir = Path("/app/generated_proto")
    output_dir.mkdir(exist_ok=True)

    # Only generate the proto files needed for speech-to-text service
    required_protos = [
        "audio.proto",
        "common.proto",
        "health/health.proto"
    ]

    success_count = 0

    # Generate Python code for required protos
    for proto_name in required_protos:
        proto_file = proto_dir / proto_name
        if not proto_file.exists():
            continue

        cmd = [
            "python", "-m", "grpc_tools.protoc",
            f"--proto_path={proto_dir}",
            f"--python_out={output_dir}",
            f"--grpc_python_out={output_dir}",
            str(proto_file)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            success_count += 1
        except subprocess.CalledProcessError as e:
            events.error("Failed to generate proto file", exception=e, metadata={"file": proto_file.name, "stderr": e.stderr})
            # Continue with other files instead of failing completely
            continue

    if success_count > 0:
        return True
    else:
        events.error("No protobuf files were generated successfully")
        return False

if __name__ == "__main__":
    success = generate_proto_files()
    sys.exit(0 if success else 1)
