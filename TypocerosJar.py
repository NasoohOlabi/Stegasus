import subprocess

class JavaJarWrapper:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._start_jar()
        return cls._instance

    def _start_jar(self):
        jar_path = "./Typoceros4j.jar"
        self._process = subprocess.Popen(["java", "-jar", jar_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

    def encode(self, string, bytes):
        if self._process.stdin is None:
          raise Exception("Error stdin is not available")
        if self._process.stdout is None:
          raise Exception("Error stdout is not available")
        self._process.stdin.write(b"encode\n")
        self._process.stdin.write(string.encode("utf-8") + b"\n")
        self._process.stdin.write(bytes.encode("utf-8") + b"\n")
        self._process.stdin.flush()

        output = self._process.stdout.readline().decode("utf-8").strip()
        remaining_bytes = self._process.stdout.readline().decode("utf-8").strip()

        return output, remaining_bytes

    def decode(self, string):
        if self._process.stdin is None:
          raise Exception("Error stdin is not available")
        if self._process.stdout is None:
          raise Exception("Error stdout is not available")
        self._process.stdin.write(b"decode\n")
        self._process.stdin.write(string.encode("utf-8") + b"\n")
        self._process.stdin.flush()

        output = self._process.stdout.readline().decode("utf-8").strip()
        values = self._process.stdout.readline().decode("utf-8").strip()

        return output, values
