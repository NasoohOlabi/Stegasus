import base64
import os
import subprocess
from typing import Tuple


class JavaJarWrapper:
  _instance = None

  def __new__(cls):
    if cls._instance is None:
      cls._instance = super().__new__(cls)
      cls._instance._start_jar()
    return cls._instance

  def _start_jar(self):
    script_directory = os.path.dirname(os.path.abspath(__file__))
    jar_path = os.path.join(script_directory, 'Typoceros4j.jar')

    java_executable = "java"
    if os.name == "posix":  # Linux system
      try:
        java_executable = subprocess.check_output(["which", "java"]).decode("utf-8").strip()
      except subprocess.CalledProcessError:
        raise Exception("Java executable not found")

    # Check if the JAR file is valid
    if not os.path.isfile(jar_path):
      raise Exception("Invalid JAR file")

    self._process = subprocess.Popen([java_executable, "-jar", jar_path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE)

  def getProcess(self):
    if self._process and self._process.poll() is None:
      return self._process
    else:
      self._start_jar()
      return self._process

  def encode(self, string, bytes_str):
    string = JavaJarWrapper.to64(string)
    try:
      process = self.getProcess()
      if process.stdin is None:
        raise Exception("Error stdin is not available")
      if process.stdout is None:
        raise Exception("Error stdout is not available")
      process.stdin.write(b"encode\n")
      process.stdin.write(string.encode("utf-8") + b"\n")
      process.stdin.write(bytes_str.encode("utf-8") + b"\n")
      process.stdin.flush()

      output = process.stdout.readline().decode("utf-8").strip()
      self.log(output)
      remaining_bytes = process.stdout.readline().decode("utf-8").strip()
      self.log(remaining_bytes)

      return JavaJarWrapper.from64(output), remaining_bytes
    except BrokenPipeError:
      self._start_jar()
      return self.encode(string, bytes_str)

  def echo(self, string):
    string = JavaJarWrapper.to64(string)
    try:
      process = self.getProcess()
      if process.stdin is None:
        raise Exception("Error stdin is not available")
      if process.stdout is None:
        raise Exception("Error stdout is not available")
      process.stdin.write(b"echo\n")
      process.stdin.write(string.encode("utf-8") + b"\n")
      process.stdin.flush()

      output = process.stdout.readline().decode("utf-8").strip()
      self.log(output)

      return JavaJarWrapper.from64(output)
    except BrokenPipeError:
      self._start_jar()
      return self.echo(string)

  def decode(self, string) -> Tuple[str, str]:
    string = JavaJarWrapper.to64(string)
    try:
      process = self.getProcess()
      if process.stdin is None:
        raise Exception("Error stdin is not available")
      if process.stdout is None:
        raise Exception("Error stdout is not available")
      process.stdin.write(b"decode\n")
      process.stdin.write(string.encode("utf-8") + b"\n")
      process.stdin.flush()

      output = process.stdout.readline().decode("utf-8").strip()
      self.log(output)
      values = process.stdout.readline().decode("utf-8").strip()
      self.log(values)

      return JavaJarWrapper.from64(output), values
    except BrokenPipeError:
      self._start_jar()
      return self.decode(string)

  @staticmethod
  def to64(s: str):
    b = base64.b64encode(bytes(s, 'utf-8'))  # bytes
    return b.decode('utf-8')  # convert bytes to string

  @staticmethod
  def from64(s: str):
    b = base64.b64decode(bytes(s, 'utf-8'))
    return b.decode('utf-8')
  
  def log(self,s:str):
    with open('Typoceros/wrapper.log','a') as o:
      o.write(s+'\n')

if __name__ == '__main__':
  Typo = JavaJarWrapper()
  r = Typo.echo("It's been interesting 😎 seeing a project 🙂 with a junior backend starting after a few 👍🏻👍🏻 months here.")

  print(r)