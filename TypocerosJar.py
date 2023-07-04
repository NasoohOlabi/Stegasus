import os
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
    java_executable = "java"
    if os.name == "posix":  # Linux system
      try:
        java_executable = subprocess.check_output(["which", "java"]).decode("utf-8").strip()
      except subprocess.CalledProcessError:
        raise Exception("Java executable not found")
    self._process = subprocess.Popen([java_executable, "-jar", jar_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  def encode(self, string, bytes_str):
    try:
      if self._process.stdin is None:
        raise Exception("Error stdin is not available")
      if self._process.stdout is None:
        raise Exception("Error stdout is not available")
      self._process.stdin.write(b"encode\n")
      self._process.stdin.write(string.encode("utf-8") + b"\n")
      self._process.stdin.write(bytes_str.encode("utf-8") + b"\n")
      self._process.stdin.flush()

      output = self._process.stdout.readline().decode("utf-8").strip()
      remaining_bytes = self._process.stdout.readline().decode("utf-8").strip()

      return output, remaining_bytes
    except BrokenPipeError:
      self._start_jar()
      return self.encode(string, bytes_str)

  def spell(self, string, bytes_str):
    try:
      if self._process.stdin is None:
        raise Exception("Error stdin is not available")
      if self._process.stdout is None:
        raise Exception("Error stdout is not available")
      self._process.stdin.write(b"spell\n")
      self._process.stdin.write(string.encode("utf-8") + b"\n")
      self._process.stdin.flush()

      output = self._process.stdout.readline().decode("utf-8").strip()

      return output
    except BrokenPipeError:
      self._start_jar()
      return self.encode(string, bytes_str)
    
  def decode(self, string):
    try:
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
    except BrokenPipeError:
      self._start_jar()
      return self.decode(string)
    
if __name__ == '__main__':
  Typo = JavaJarWrapper()
  r = Typo.encode("hi, how are you?","010101101010001011010")

  print(r)