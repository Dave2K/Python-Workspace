import os
import sys

def split_file_by_bytes(input_file, chunk_size):
    with open(input_file, 'rb') as f:
        part = 1
        while True:
            data = f.read(chunk_size)
            if not data:
                break
            output_file = f"{input_file}_part{part}"
            with open(output_file, 'wb') as out:
                out.write(data)
            print(f"Wrote: {output_file} ({len(data)} bytes)")
            part += 1

if __name__ == "__main__":
    script_name = os.path.basename(sys.argv[0])
    
    if len(sys.argv) < 3:
        print(f"Usage: python {script_name} <input_file> <chunk_size_in_bytes>")
        sys.exit(1)
    
    input_file = sys.argv[1]
    try:
        chunk_size = int(sys.argv[2])
    except ValueError:
        print("Chunk size must be an integer.")
        sys.exit(1)
    
    if not os.path.exists(input_file):
        print(f"File {input_file} not found.")
        sys.exit(1)
    
    split_file_by_bytes(input_file, chunk_size)
