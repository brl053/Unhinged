#!/usr/bin/env python3
"""
Generate protobuf files for speech-to-text service
"""
import subprocess
import sys
import os
from pathlib import Path

def generate_proto_files():
    """Generate protobuf files from proto definitions"""

    # Find proto files
    proto_dir = Path("/app/proto")
    if not proto_dir.exists():
        print(f"Proto directory not found: {proto_dir}")
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
            print(f"⚠️ Proto file not found: {proto_file}")
            continue

        print(f"Generating Python code for {proto_file}")

        cmd = [
            "python", "-m", "grpc_tools.protoc",
            f"--proto_path={proto_dir}",
            f"--python_out={output_dir}",
            f"--grpc_python_out={output_dir}",
            str(proto_file)
        ]

        try:
            result = subprocess.run(cmd, capture_output=True, text=True, check=True)
            print(f"✅ Generated: {proto_file.name}")
            success_count += 1
        except subprocess.CalledProcessError as e:
            print(f"❌ Failed to generate {proto_file.name}: {e}")
            print(f"stderr: {e.stderr}")
            # Continue with other files instead of failing completely
            continue

    if success_count > 0:
        print(f"✅ Generated {success_count} protobuf files successfully")
        return True
    else:
        print("❌ No protobuf files were generated successfully")
        return False

if __name__ == "__main__":
    success = generate_proto_files()
    sys.exit(0 if success else 1)
