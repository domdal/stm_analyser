import os
from multiprocessing import Pool
import subprocess

# project = "L4R5ZI"
# board = "NUCLEO-L4R5ZI"
# stm_series = 'stm32l4'

project = "L432KC"
board = "NUCLEO-L432KC"
stm_series = 'stm32l4'

# project = "STM32F746G"
# board = "STM32F746G-DISCO"
# stm_series = 'stm32f4'

stm_ai = "C:/Users/Dominik/STM32Cube/Repository/Packs/STMicroelectronics/X-CUBE-AI/8.0.0/Utilities/windows/stm32ai"
ofa_path = 'C:\\Users\\Dominik\\git\\matthias_stm_auswertung\\ofa_nets\\ofa_NAS_TEST1\\' + board + '\\'

def cubeia_task(argument):
    command, path = argument
    p = subprocess.Popen(command, cwd=path)
    p.wait()
    
if __name__ == "__main__":

    pool = Pool(processes=4)
    arguments = []

    for path in os.listdir(ofa_path):
        for file in os.listdir(ofa_path + path):
            if "analyze_output" in os.listdir(ofa_path + path):
                print("Skipping " + ofa_path + path)
                continue
            elif file.endswith(".onnx"):
                new_onnx_model = ofa_path + path + '\\' + file
                onnx_path = ofa_path + path + '\\'
                command = [stm_ai, "analyze", "--name", "network", "-m", new_onnx_model, "--type", "onnx", "--compression", "none", "--verbosity", "1", "--output", onnx_path, "--allocate-inputs", "--series", stm_series, "--allocate-outputs"]
                arguments.append([command, onnx_path]) 
    pool.imap(cubeia_task, arguments)
    # shutdown the process pool
    pool.close()
    # wait for all issued task to complete
    pool.join()
    exit()
