import subprocess
import os
import shutil
import time
import serial

# project = "L4R5ZI"
# board = "NUCLEO-L4R5ZI"
# stm_port = 'COM7'
# baudrate = 209700
# parity = serial.PARITY_NONE
# stopbits = serial.STOPBITS_ONE
# bytesize = serial.SEVENBITS

# project = "L432KC"
# board = "NUCLEO-L432KC"
# stm_port = 'COM8'
# baudrate = 209700
# parity = serial.PARITY_NONE
# stopbits = serial.STOPBITS_ONE
# bytesize = serial.SEVENBITS

project = "STM32F746G"
board = "STM32F746G-DISCO"
stm_port = 'COM9'
baudrate = 115200
parity = serial.PARITY_NONE
stopbits = serial.STOPBITS_ONE
bytesize = serial.EIGHTBITS

onnx_model = 'C:\\Users\\Dominik\\git\\stm_analyser\\onnx_model\\model.onnx'
stm_exe = 'C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeMX\\STM32CubeMX.exe'
stm_script = 'C:\\Users\\Dominik\\git\\stm_analyser\\project_script.txt'
make_exe = 'C:\\Program Files (x86)\\GnuWin32\\bin\\make.exe'
stm32ai_exe = 'C:\\Users\\Dominik\\STM32Cube\\Repository\\Packs\\STMicroelectronics\\X-CUBE-AI\\8.0.0\\Utilities\\windows\\stm32ai.exe'
ofa_path = 'C:\\Users\\Dominik\\git\\stm_analyser\\ofa_nets\\ofa_NAS_TEST3\\' + board + '\\'
stm_prog_exe = 'C:\\Program Files\\STMicroelectronics\\STM32Cube\\STM32CubeProgrammer\\bin\\STM32_Programmer_CLI.exe'

generate_path = 'C:\\Users\\Dominik\\git\\stm_analyser\\project\\' + project + '_generate\\' + project + '\\Makefile'
generate_project = 'C:\\Users\\Dominik\\git\\stm_analyser\\project\\' + project + '_generate\\' + project
bin_file = 'C:\\Users\\Dominik\\git\\stm_analyser\\project\\' + project + '_generate\\' + project + '\\build\\' + project + '.bin'


def run_eval(new_onnx_model, onnx_path):

    shutil.copy(new_onnx_model, onnx_model)

    line = "config load C:\\Users\\Dominik\\git\\stm_analyser\\project\\" + project + "\\" + project + ".ioc\n" + \
    "project path C:\\Users\\Dominik\\git\\stm_analyser\\project\\" + project + "_generate\n" + \
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

    time.sleep(20)

    #insert the most important line of the world into the stm generate garbage
    if project == "STM32F746G":
        import fileinput
        # Specify the file path and the string to insert
    
        file_path = "C:\\Users\\Dominik\\git\\stm_analyser\\project\\STM32F746G_generate\\STM32F746G\\Core\\Src\\main.c"
        insert_string = "MX_X_CUBE_AI_Process();\n"

        # Open the file for reading and writing
        with fileinput.FileInput(file_path, inplace=True) as file:
            # Iterate through every line in the file
            for line in file:
                # If the line contains "osDelay(1);", insert the new string before it
                if "osDelay(1);" in line:
                    print(insert_string, end='')
                # Print the current line to the file (with automatic line ending)
                print(line, end='')

    os.remove(stm_script)
    
    command = [make_exe]
    p = subprocess.Popen(command, cwd=generate_project, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    output = str(output.decode())
    err = str(err.decode())
    p.wait()
    print(output)
    print(err)
    
    if "region `FLASH\' overflowed" in str(err):
        print("FLASH overflowed!")
        with open(onnx_path + 'flash_overflow.txt', 'w') as fp:
            fp.write(output + err)
        shutil.rmtree(generate_project)
        return
    
    if "region `RAM\' overflowed" in str(err):
        print("RAM overflowed!")
        with open(onnx_path + 'ram_overflow.txt', 'w') as fp:
            fp.write(output + err)
        shutil.rmtree(generate_project)
        return
    
    

    while(os.path.isfile(bin_file) == False):
        print("Waiting for bin file to be generated...")
        time.sleep(5)
        pass

    print("Bin File generated!")

    command = [stm_prog_exe, "-c", "port=SWD", "-w", bin_file, "0x08000000", "-rst"]
    p = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    output, err = p.communicate()
    output = str(output)
    err = str(err)
    p.wait()
    print(output)
    print(err)

    with open(onnx_path + 'stm_prog_log.txt', 'w') as fp:
            fp.write(output + err)

    shutil.rmtree(generate_project)

    print("Starting evaluation...")

    ser = serial.Serial(
        port=stm_port,
        baudrate=baudrate,
        parity=parity,
        stopbits=stopbits,
        bytesize=bytesize)

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
            if "result.txt" in os.listdir(ofa_path + path) or "ram_overflow.txt" in os.listdir(ofa_path + path) or "flash_overflow.txt" in os.listdir(ofa_path + path):
                print("Skipping " + ofa_path + path)
                continue
            if file.endswith(".onnx"):
                new_onnx_model = ofa_path + path + '\\' + file
                onnx_path = ofa_path + path + '\\'
                print("Using model: " + new_onnx_model)
                print("Using path: " + onnx_path)
                run_eval(new_onnx_model, onnx_path)
