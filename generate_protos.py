import os
import subprocess
import sys

def main():
    proto_dir = "packages/protocols/protos"
    out_dir = "packages/protocols/src/strata_protocols"
    proto_file = "agent_service.proto"

    # Command to run grpc_tools.protoc
    cmd = [
        sys.executable, "-m", "grpc_tools.protoc",
        f"-I{proto_dir}",
        f"--python_out={out_dir}",
        f"--grpc_python_out={out_dir}",
        os.path.join(proto_dir, proto_file)
    ]

    print(f"Running: {' '.join(cmd)}")
    subprocess.run(cmd, check=True)
    
    # Post-process to fix imports in generated grpc file
    grpc_file = os.path.join(out_dir, "agent_service_pb2_grpc.py")
    with open(grpc_file, "r") as f:
        content = f.read()
    
    # grpc_tools generates `import agent_service_pb2 as agent__service__pb2`
    # We need it to be relative: `from . import agent_service_pb2 as agent__service__pb2`
    content = content.replace("import agent_service_pb2 as agent__service__pb2", "from . import agent_service_pb2 as agent__service__pb2")
    
    with open(grpc_file, "w") as f:
        f.write(content)
        
    print("Protos generated successfully.")

if __name__ == "__main__":
    main()
