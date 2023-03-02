import subprocess
import os
import shutil
import time
import serial

# project = "L4R5ZI"
# board = "NUCLEO-L4R5ZI"
#stm_port = 'COM7'


project = "L432KC"
board = "NUCLEO-L432KC"
stm_port = 'COM8'


# project = "STM32F746G"
# board = "STM32F746G-DISCO"
# port = 'COM9'

onnx_model = 'C:\\Users\\Dominik\\git\\matthias_stm_auswertung\\onnx_model\\model.onnx'
stm_exe = 'C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeMX\\STM32CubeMX.exe'
stm_script = 'C:\\Users\\Dominik\\git\\matthias_stm_auswertung\\project_script.txt'
make_exe = 'C:\\Program Files (x86)\\GnuWin32\\bin\\make.exe'
stm32ai_exe = 'C:\\Users\\Dominik\\STM32Cube\\Repository\\Packs\\STMicroelectronics\\X-CUBE-AI\\8.0.0\\Utilities\\windows\\stm32ai.exe'
ofa_path = 'C:\\Users\\Dominik\\git\\matthias_stm_auswertung\\ofa_nets\\ofa_NAS_TEST1\\' + board + '\\'
stm_prog_exe = 'C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeProgrammer\\bin\\STM32_Programmer_CLI.exe'

generate_path = 'C:\\Users\\Dominik\\git\\matthias_stm_auswertung\\project\\' + project + '_generate\\' + project + '\\Makefile'
generate_project = 'C:\\Users\\Dominik\\git\\matthias_stm_auswertung\\project\\' + project + '_generate\\' + project
bin_file = 'C:\\Users\\Dominik\\git\\matthias_stm_auswertung\\project\\' + project + '_generate\\' + project + '\\build\\' + project + '.bin'


def run_eval(new_onnx_model, onnx_path):

    shutil.copy(new_onnx_model, onnx_model)

    line = "config load C:\\Users\\Dominik\\git\\matthias_stm_auswertung\\project\\" + project + "\\" + project + ".ioc\n" + \
    "project path C:\\Users\\Dominik\\git\\matthias_stm_auswertung\\project\\" + project + "_generate\n" + \
    "project generate\n" + \
    "exit\n"

    with open(stm_script, "w") as f:
        f.write(line)

    command = [stm_exe, "-q", stm_script]

    p = subprocess.Popen(command)
    p.wait()

    while(os.path.isfile(generate_path) == False):
        print("Waiting for file to be generated...")
        time.sleep(5)
        pass

    print("File generated!")
    os.remove(stm_script)

    time.sleep(10)

    command = [make_exe]
    p = subprocess.Popen(command, cwd=generate_project)
    p.wait()

    while(os.path.isfile(bin_file) == False):
        print("Waiting for bin file to be generated...")
        time.sleep(5)
        pass

    print("Bin File generated!")

    command = [stm_prog_exe, "-c", "port=SWD", "-w", bin_file, "0x08000000", "-rst"]
    p = subprocess.Popen(command)
    p.wait()

    shutil.rmtree(generate_project)

    # print("Copying bin file to STM32...")
    # now = time.time()
    # shutil.copy(bin_file, stm_drive)
    # time_nedded = int(time.time() - now)
    # print("Copy time = " + str(time.time() - now))
    # print("Bin File copied!")
    # shutil.rmtree(generate_project)

    # print("Microcontroller programmed!")
    # print(f"Waiting {time_nedded} s because stm is stm")
    # time.sleep(time_nedded)

    # #Connection resets the STM, otherwise it is some kind of boot loop
    # command = [stm_prog_exe, "-c", "port=SWD"]
    # subprocess.Popen(command)

    print("Starting evaluation...")

    ser = serial.Serial(
        port=stm_port,
        baudrate=209700,
        parity=serial.PARITY_NONE,
        stopbits=serial.STOPBITS_ONE,
        bytesize=serial.SEVENBITS)

    result = ""
    first_line = False

    while(1):
        line = str(ser.readline().decode())
        print(line)
        if 'Running PerfTest on ' in line:
            if first_line == False:
                first_line = True
            else:
                break
        if first_line == True:
            result += line
    
    ser.close()

    with open(onnx_path + "result.txt", "w") as text_file:
        text_file.write(result)

if __name__ == "__main__":
    # new_onnx_model = 'C:\\Users\\Dominik\\git\\matthias_stm_auswertung\\ofa_nets\\ofa_NAS_TEST1\\NUCLEO-L4R5ZI\\Beef\\KBPeakMemory_618KBFlash_1981.onnx'
    # onnx_path = 'C:\\Users\\Dominik\\git\\matthias_stm_auswertung\\ofa_nets\\ofa_NAS_TEST1\\NUCLEO-L4R5ZI\\Beef\\'
    # run_eval(new_onnx_model, onnx_path)
    for path in os.listdir(ofa_path):
        for file in os.listdir(ofa_path + path):
            if "result.txt" in os.listdir(ofa_path + path):
                print("Skipping " + ofa_path + path)
                continue
            if file.endswith(".onnx"):
                new_onnx_model = ofa_path + path + '\\' + file
                onnx_path = ofa_path + path + '\\'
                print("Using model: " + new_onnx_model)
                print("Using path: " + onnx_path)
                run_eval(new_onnx_model, onnx_path)
