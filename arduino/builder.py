import json
import os
import platform as os_platform
import shutil
import subprocess
import multiprocessing as os_multiprocessing
from datetime import datetime
from enum import Enum
from typing import List, Set
import sys
import time
import select
import wx

# List of OPLC dependencies
# This list can be reduced, as soon as the HALs list provides board specific library dependencies.
OPLC_DEPS = [
    'WiFiNINA',
    'Ethernet',
    'Arduino_MachineControl',
    'Arduino_EdgeControl',
    'OneWire',
    'DallasTemperature',
    'P1AM',
    'CONTROLLINO',
    'PubSubClient',
    'ArduinoJson',
    'arduinomqttclient',
    'RP2040_PWM',
    'AVR_PWM',
    'megaAVR_PWM',
    'SAMD_PWM',
    'SAMDUE_PWM',
    'Portenta_H7_PWM',
    'CAN',
    'STM32_CAN',
    'STM32_PWM'
]


global compiler_logs
compiler_logs = ''

global base_path
base_path = 'editor/arduino/src/'

class BuildCacheOption(Enum):
    USE_CACHE = 0
    CLEAN_BUILD = 1
    CLEAN_LIB = 2
    CLEAN_ALL = 3

    def __lt__(self, other):
        if self.__class__ is other.__class__:
            return self.value < other.value
        return NotImplemented

    def __le__(self, other):
        if self.__class__ is other.__class__:
            return self.value <= other.value
        return NotImplemented

    def __gt__(self, other):
        if self.__class__ is other.__class__:
            return self.value > other.value
        return NotImplemented

    def __ge__(self, other):
        if self.__class__ is other.__class__:
            return self.value >= other.value
        return NotImplemented

    def __eq__(self, other):
        if self.__class__ is other.__class__:
            return self.value == other.value
        return NotImplemented

    def __ne__(self, other):
        if self.__class__ is other.__class__:
            return self.value != other.value
        return NotImplemented


def append_compiler_log(send_text, output):
    global compiler_logs
    compiler_logs += output

    log_file_path = os.path.join(base_path, 'build.log')
    try:
        with open(log_file_path, 'a', newline='') as log_file:
            lines = output.splitlines()
            for line in lines:
                timestamp = datetime.now().isoformat(timespec='milliseconds')
                log_file.write(f"[{timestamp}] {line}\n")
    except IOError as e:
        print(f"Fehler beim Schreiben in die Logdatei: {e}")

    send_text(output)

def runCommand(command):
    cmd_response = None

    try:
        cmd_response = subprocess.check_output(command, shell=True, stderr=subprocess.STDOUT)
    except subprocess.CalledProcessError as exc:
        cmd_response = exc.output

    if cmd_response == None:
        return ''

    return cmd_response.decode('utf-8', errors='backslashreplace')

def read_output(process, send_text, timeout=None):
    start_time = time.time()
    return_code = 0

    while True:
        output = process.stdout.readline()
        if output:
            append_compiler_log(send_text, output)
            wx.YieldIfNeeded()

        # check for process exit
        poll_result = process.poll()
        if poll_result is not None:
            # process terminated, read remaining output data
            for line in process.stdout:
                append_compiler_log(send_text, line)
                wx.YieldIfNeeded()
            return_code = poll_result
            break

        # watch for the timeout
        if (timeout is not None) and ((time.time() - start_time) > timeout):
            process.kill()
            return_code = -1  # timeout error code
            break

        # brief sleep to reduce CPU load
        time.sleep(0.02)

    return return_code


def runCommandToWin(send_text, command, cwd=None, timeout=None):
    return_code = -2  # default value for unexpected errors
    append_compiler_log(send_text, '$ ' + ' '.join(map(str, command)) + '\n')

    popenargs = {
            "cwd":    os.getcwd() if cwd is None else cwd,
            "stdout": subprocess.PIPE,
            "stderr": subprocess.STDOUT,
            "bufsize": 1,
            "universal_newlines": True,
            "close_fds": True,
            "encoding": "utf-8",
            "errors": "backslashreplace"
        }

    try:
        # add extra flags for Windows
        if os.name in ("nt", "ce"):
            popenargs["creationflags"] = subprocess.CREATE_NO_WINDOW

        # start the sub process
        compilation = subprocess.Popen(command, **popenargs)

        return_code = read_output(compilation, send_text, timeout)
        append_compiler_log(send_text, '$? = ' + str(return_code) + '\n')

    except subprocess.CalledProcessError as exc:
        append_compiler_log(send_text, exc.output)
        return_code = exc.returncode if exc.returncode is not None else -3

    return return_code

def log_host_info(send_text):
    # Number of logical CPU cores
    logical_cores = os_multiprocessing.cpu_count()

    # System architecture
    architecture = os_platform.architecture()[0]

    # Processor name
    processor = os_platform.processor()

    # Operating system
    os_name = os_platform.system()

    append_compiler_log(send_text, f"Host architecture: {architecture}\n")
    append_compiler_log(send_text, f"Processor: {processor}\n")
    append_compiler_log(send_text, f"Logical CPU cores: {logical_cores}\n")
    append_compiler_log(send_text, f"Operating system: {os_name}\n")

    # Additional information for Linux systems
    if os_name == "Linux":
        try:
            with open("/proc/cpuinfo", "r") as f:
                cpu_info = f.read()

            # Physical cores (rough estimate)
            physical_cores = len([line for line in cpu_info.split('\n') if line.startswith("physical id")])
            append_compiler_log(send_text, f"Estimated physical CPU cores: {physical_cores or 'Not available'}\n")

            # CPU frequency
            cpu_mhz = [line for line in cpu_info.split('\n') if "cpu MHz" in line]
            if cpu_mhz:
                append_compiler_log(send_text, f"CPU frequency: {cpu_mhz[0].split(':')[1].strip()} MHz\n")
            else:
                append_compiler_log(send_text, "CPU frequency: Not available\n")

        except Exception as e:
            append_compiler_log(send_text, f"Error reading /proc/cpuinfo: {e}\n")

    # Additional information for macOS systems
    elif os_name == "Darwin":  # Darwin is the core of macOS
        try:
            # Physical cores
            physical_cores = int(subprocess.check_output(["sysctl", "-n", "hw.physicalcpu"]).decode().strip())
            append_compiler_log(send_text, f"Physical CPU cores: {physical_cores}\n")

            # CPU frequency
            cpu_freq = subprocess.check_output(["sysctl", "-n", "hw.cpufrequency"]).decode().strip()
            cpu_freq_mhz = int(cpu_freq) / 1000000  # Convert Hz to MHz
            append_compiler_log(send_text, f"CPU frequency: {cpu_freq_mhz:.2f} MHz\n")

            # CPU model
            cpu_model = subprocess.check_output(["sysctl", "-n", "machdep.cpu.brand_string"]).decode().strip()
            append_compiler_log(send_text, f"CPU model: {cpu_model}\n")

        except Exception as e:
            append_compiler_log(send_text, f"Error getting macOS CPU info: {e}\n")

    path_content = os.environ.get('PATH', '')
    append_compiler_log(send_text, "\n" + _("active PATH Variable") + ":\n" + path_content + "\n\n")

def get_installed_libraries(cli_command_str) -> List[str]:
    #print("Executing command:", cli_command_str + " lib list --json")
    libraries_json = runCommand(cli_command_str + " lib list --json")

    try:
        libraries_data = json.loads(libraries_json)
        installed_libs = []

        for lib in libraries_data.get("installed_libraries", []):
            lib_name = lib.get("library", {}).get("name")
            if lib_name:
                installed_libs.append(lib_name)

        #print("Installed libraries:", installed_libs)
        return installed_libs
    except json.JSONDecodeError as e:
        print("Error decoding JSON:", e)
        print("Raw JSON output:", libraries_json)
        return []
    except Exception as e:
        print("An error occurred:", e)
        return []

def clean_libraries(send_text, cli_command):
    # the intended behavior is to keep the list of installed libraries identical, but remove all and re-install all of them
    return_code = 0
    append_compiler_log(send_text, _("Cleaning libraries") + "...\n")
    installed_libraries = get_installed_libraries(' '.join(cli_command))

    # Merge installed libraries with OPLC_DEPS and remove duplicates
    all_libraries: Set[str] = set(installed_libraries + OPLC_DEPS)

    for lib in all_libraries:
        append_compiler_log(send_text, f"Processing library: {lib}\n")
        runCommandToWin(send_text, cli_command + ['lib', 'uninstall', lib])
        return_code = runCommandToWin(send_text, cli_command + ['lib', 'install', lib])
        if (return_code != 0):
            append_compiler_log(send_text, '\n' + _('LIBRARIES INSTALLATION FAILED') + ': ' + lib + '\n')
            return

    return return_code

def build(st_file, platform, source_file, port, send_text, hals, build_option):
    global base_path
    global compiler_logs
    compiler_logs = ''

    open(os.path.join(base_path, 'build.log'), 'w').close() # truncate the build.log file
    log_host_info(send_text)

    #Check if board is installed
    board_installed = False
    core = ''
    for board in hals:
        if hals[board]['platform'] == platform:
            core = hals[board]['core']
            if hals[board]['version'] != "0":
                board_installed = True

    #Check MatIEC compiler
    if (os.path.exists("editor/arduino/bin/iec2c") or os.path.exists("editor/arduino/bin/iec2c.exe") or os.path.exists("editor/arduino/bin/iec2c_mac")):
        # remove old files first
        if os.path.exists('editor/arduino/src/POUS.c'):
            os.remove('editor/arduino/src/POUS.c')
        if os.path.exists('editor/arduino/src/POUS.h'):
            os.remove('editor/arduino/src/POUS.h')
        if os.path.exists('editor/arduino/src/LOCATED_VARIABLES.h'):
            os.remove('editor/arduino/src/LOCATED_VARIABLES.h')
        if os.path.exists('editor/arduino/src/VARIABLES.csv'):
            os.remove('editor/arduino/src/VARIABLES.csv')
        if os.path.exists('editor/arduino/src/Config0.c'):
            os.remove('editor/arduino/src/Config0.c')
        if os.path.exists('editor/arduino/src/Config0.h'):
            os.remove('editor/arduino/src/Config0.h')
        if os.path.exists('editor/arduino/src/Res0.c'):
            os.remove('editor/arduino/src/Res0.c')
    else:
        append_compiler_log(send_text, _("Error: iec2c compiler not found!") + '\n')
        return

    cli_command = []
    if os_platform.system() == 'Windows':
        cli_command = ['editor\\arduino\\bin\\arduino-cli-w64', '--no-color']
    elif os_platform.system() == 'Darwin':
        cli_command = ['editor/arduino/bin/arduino-cli-mac', '--no-color']
    else:
        cli_command = ['editor/arduino/bin/arduino-cli-l64', '--no-color']

    #Install/Update board support
    if not board_installed or build_option >= BuildCacheOption.CLEAN_ALL:
        append_compiler_log(send_text, _("Cleaning download cache") + "...\n")
        runCommandToWin(send_text, cli_command + ['cache', 'clean'])

        if board_installed == False:
            append_compiler_log(send_text, _("Support for {platform} is not installed on OpenPLC Editor. Please be patient and wait while {platform} is being installed...").format(platform=platform) + '\n')
        elif build_option >= BuildCacheOption.CLEAN_ALL:
            append_compiler_log(send_text, _("Updating support for {platform}. Please be patient and wait while {platform} is being installed...").format(platform=platform) + '\n')

        """
        ### ARDUINO-CLI CHEAT SHEET ###

        1. List installed boards:
          => arduino-cli board listall

        2. Search for a core (even if not installed yet):
          => arduino-cli core search [search text]

        3. Dump current configuration:
          => arduino-cli config dump

        4. Get additional board parameters:
          => arduino-cli board details -fqbn [board fqbn]
        """

        # Initialize arduino-cli config - if it hasn't been initialized yet
        return_code = runCommandToWin(send_text, cli_command + ['config', 'init'])

        # Setup boards - remove 3rd party boards to re-add them later since we don't know if they're there or not
        return_code = runCommandToWin(send_text, cli_command + ['config', 'remove', 'board_manager.additional_urls',
            'https://arduino.esp8266.com/stable/package_esp8266com_index.json',
            'https://espressif.github.io/arduino-esp32/package_esp32_index.json',
            'https://github.com/stm32duino/BoardManagerFiles/raw/main/package_stmicroelectronics_index.json',
            'https://raw.githubusercontent.com/CONTROLLINO-PLC/CONTROLLINO_Library/master/Boards/package_ControllinoHardware_index.json',
            'https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json',
            'https://facts-engineering.gitlab.io/facts-open-source/p1am/beta_file_hosting/package_productivity-P1AM_200-boardmanagermodule_index.json',
            'https://raw.githubusercontent.com/VEA-SRL/IRUINO_Library/main/package_vea_index.json',
            'https://raw.githubusercontent.com/facts-engineering/facts-engineering.github.io/master/package_productivity-P1AM-boardmanagermodule_index.json'])

        # Setup boards - add 3rd party boards
        return_code = runCommandToWin(send_text, cli_command + ['config', 'add', 'board_manager.additional_urls',
            'https://arduino.esp8266.com/stable/package_esp8266com_index.json',
            'https://espressif.github.io/arduino-esp32/package_esp32_index.json',
            'https://github.com/stm32duino/BoardManagerFiles/raw/main/package_stmicroelectronics_index.json',
            'https://raw.githubusercontent.com/CONTROLLINO-PLC/CONTROLLINO_Library/master/Boards/package_ControllinoHardware_index.json',
            'https://github.com/earlephilhower/arduino-pico/releases/download/global/package_rp2040_index.json',
            'https://facts-engineering.gitlab.io/facts-open-source/p1am/beta_file_hosting/package_productivity-P1AM_200-boardmanagermodule_index.json',
            'https://raw.githubusercontent.com/facts-engineering/facts-engineering.github.io/master/package_productivity-P1AM-boardmanagermodule_index.json',
            'https://raw.githubusercontent.com/VEA-SRL/IRUINO_Library/main/package_vea_index.json'])

        if (return_code != 0):
            append_compiler_log(send_text, '\n' + _('BOARD INSTALLATION FAILED!') + '\n')
            return

        # Update
        return_code = runCommandToWin(send_text, cli_command + ['core', 'update-index'])
        if (return_code != 0):
            append_compiler_log(send_text, '\n' + _('INDEX UPDATE FAILED!') + '\n')
            return

        return_code = runCommandToWin(send_text, cli_command + ['update'])
        if (return_code != 0):
            append_compiler_log(send_text, '\n' + _('CORE or LIBRARIES UPDATE FAILED!') + '\n')
            return

        # Install board
        return_code = runCommandToWin(send_text, cli_command + ['core', 'install', core])
        if (return_code != 0):
            append_compiler_log(send_text, '\n' + _('CORE INSTALLATION FAILED!') + '\n')
            return

    if build_option >= BuildCacheOption.CLEAN_LIB:
        # Install all libs - required after core install/update and for clean libraries
        return_code = clean_libraries(send_text, cli_command)

    # Generate C files
    append_compiler_log(send_text, _("Compiling .st file...") + '\n')
    if (os.name == 'nt'):
        base_path = 'editor\\arduino\\src\\'
    else:
        base_path = 'editor/arduino/src/'
    f = open(base_path+'plc_prog.st', 'w')
    f.write(st_file)
    f.flush()
    f.close()

    time.sleep(0.2)  # make sure plc_prog.st was written to disk

    if os_platform.system() == 'Windows':
        return_code = runCommandToWin(send_text, ['editor\\arduino\\bin\\iec2c.exe', '-f', '-l', '-p', 'plc_prog.st'], cwd='editor\\arduino\\src')
    elif os_platform.system() == 'Darwin':
        return_code = runCommandToWin(send_text, ['../bin/iec2c_mac', '-f', '-l', '-p', 'plc_prog.st'], cwd='./editor/arduino/src')
    else:
        return_code = runCommandToWin(send_text, ['../bin/iec2c', '-f', '-l', '-p', 'plc_prog.st'], cwd='./editor/arduino/src')

    # Remove temporary plc program
    # if os.path.exists(base_path+'plc_prog.st'):
    #    os.remove(base_path+'plc_prog.st')

    # Generate glueVars.c
    if not (os.path.exists(base_path+'LOCATED_VARIABLES.h')):
        append_compiler_log(send_text, "Error: Couldn't find LOCATED_VARIABLES.h. Check iec2c compiler output for more information\n")
        return

    located_vars_file = open(base_path+'LOCATED_VARIABLES.h', 'r')
    located_vars = located_vars_file.readlines()
    glueVars = """
#include "iec_std_lib.h"

#define __LOCATED_VAR(type, name, ...) type __##name;
#include "LOCATED_VARIABLES.h"
#undef __LOCATED_VAR
#define __LOCATED_VAR(type, name, ...) type* name = &__##name;
#include "LOCATED_VARIABLES.h"
#undef __LOCATED_VAR

TIME __CURRENT_TIME;
BOOL __DEBUG;
extern unsigned long long common_ticktime__;

//OpenPLC Buffers
#if defined(__AVR_ATmega328P__) || defined(__AVR_ATmega168__) || defined(__AVR_ATmega32U4__) || defined(__AVR_ATmega16U4__)

#define MAX_DIGITAL_INPUT          8
#define MAX_DIGITAL_OUTPUT         32
#define MAX_ANALOG_INPUT           6
#define MAX_ANALOG_OUTPUT          32
#define MAX_MEMORY_WORD            0
#define MAX_MEMORY_DWORD           0
#define MAX_MEMORY_LWORD           0

IEC_BOOL *bool_input[MAX_DIGITAL_INPUT/8][8];
IEC_BOOL *bool_output[MAX_DIGITAL_OUTPUT/8][8];
IEC_UINT *int_input[MAX_ANALOG_INPUT];
IEC_UINT *int_output[MAX_ANALOG_OUTPUT];

#else

#define MAX_DIGITAL_INPUT          56
#define MAX_DIGITAL_OUTPUT         56
#define MAX_ANALOG_INPUT           32
#define MAX_ANALOG_OUTPUT          32
#define MAX_MEMORY_WORD            20
#define MAX_MEMORY_DWORD           20
#define MAX_MEMORY_LWORD           20

IEC_BOOL *bool_input[MAX_DIGITAL_INPUT/8][8];
IEC_BOOL *bool_output[MAX_DIGITAL_OUTPUT/8][8];
IEC_UINT *int_input[MAX_ANALOG_INPUT];
IEC_UINT *int_output[MAX_ANALOG_OUTPUT];
IEC_UINT *int_memory[MAX_MEMORY_WORD];
IEC_UDINT *dint_memory[MAX_MEMORY_DWORD];
IEC_ULINT *lint_memory[MAX_MEMORY_LWORD];

#endif


void glueVars()
{
"""
    for located_var in located_vars:
        # cleanup located var line
        if ('__LOCATED_VAR(' in located_var):
            located_var = located_var.split('(')[1].split(')')[0]
            var_data = located_var.split(',')
            if (len(var_data) < 5):
                append_compiler_log(send_text, _('Error processing located var line: {var_line_text}').format(var_line_text=located_var) + '\n')
            else:
                var_type = var_data[0]
                var_name = var_data[1]
                var_address = var_data[4]
                var_subaddress = '0'
                if (len(var_data) > 5):
                    var_subaddress = var_data[5]

                # check variable type and assign to correct buffer pointer
                if ('QX' in var_name):
                    if (int(var_address) > 6 or int(var_subaddress) > 7):
                        append_compiler_log(send_text, _('Error: wrong location for var {var_name}').format(var_name=var_name) + '\n')
                        return
                    glueVars += '    bool_output[' + var_address + \
                        '][' + var_subaddress + '] = ' + var_name + ';\n'
                elif ('IX' in var_name):
                    if (int(var_address) > 6 or int(var_subaddress) > 7):
                        append_compiler_log(send_text, _('Error: wrong location for var {var_name}').format(var_name=var_name) + '\n')
                        return
                    glueVars += '    bool_input[' + var_address + \
                        '][' + var_subaddress + '] = ' + var_name + ';\n'
                elif ('QW' in var_name):
                    if (int(var_address) > 32):
                        append_compiler_log(send_text, _('Error: wrong location for var {var_name}').format(var_name=var_name) + '\n')
                        return
                    glueVars += '    int_output[' + \
                        var_address + '] = ' + var_name + ';\n'
                elif ('IW' in var_name):
                    if (int(var_address) > 32):
                        append_compiler_log(send_text, _('Error: wrong location for var {var_name}').format(var_name=var_name) + '\n')
                        return
                    glueVars += '    int_input[' + \
                        var_address + '] = ' + var_name + ';\n'
                elif ('MW' in var_name):
                    if (int(var_address) > 20):
                        append_compiler_log(send_text, _('Error: wrong location for var {var_name}').format(var_name=var_name) + '\n')
                        return
                    glueVars += '    int_memory[' + \
                        var_address + '] = ' + var_name + ';\n'
                elif ('MD' in var_name):
                    if (int(var_address) > 20):
                        append_compiler_log(send_text, _('Error: wrong location for var {var_name}').format(var_name=var_name) + '\n')
                        return
                    glueVars += '    dint_memory[' + \
                        var_address + '] = ' + var_name + ';\n'
                elif ('ML' in var_name):
                    if (int(var_address) > 20):
                        append_compiler_log(send_text, _('Error: wrong location for var {var_name}').format(var_name=var_name) + '\n')
                        return
                    glueVars += '    lint_memory[' + \
                        var_address + '] = ' + var_name + ';\n'
                else:
                    append_compiler_log(send_text, _('Could not process location "{var_name}" from line: {var_line_text}').format(var_name=var_name, var_line_text=located_var) + '\n')
                    return

    glueVars += """
}

void updateTime()
{
    __CURRENT_TIME.tv_nsec += common_ticktime__;

    if (__CURRENT_TIME.tv_nsec >= 1000000000)
    {
        __CURRENT_TIME.tv_nsec -= 1000000000;
        __CURRENT_TIME.tv_sec += 1;
    }
}
    """
    f = open(base_path+'glueVars.c', 'w')
    f.write(glueVars)
    f.flush()
    f.close()

    time.sleep(2)  # make sure glueVars.c was written to disk

    # Patch POUS.c to include POUS.h
    f = open(base_path+'POUS.c', 'r')
    pous_c = '#include "POUS.h"\n\n' + f.read()
    f.close()

    f = open(base_path+'POUS.c', 'w')
    f.write(pous_c)
    f.flush()
    f.close()

    # Patch Res0.c to include POUS.h instead of POUS.c
    f = open(base_path+'Res0.c', 'r')
    res0_c = ''
    lines = f.readlines()
    for line in lines:
        if '#include "POUS.c"' in line:
            res0_c += '#include "POUS.h"\n'
        else:
            res0_c += line
    f.close()

    f = open(base_path+'Res0.c', 'w')
    f.write(res0_c)
    f.flush()
    f.close()

    # Copy HAL file
    if os_platform.system() == 'Windows':
        source_path = 'editor\\arduino\\src\\hal\\'
        destination = 'editor\\arduino\\src\\arduino.cpp'
    else:
        source_path = 'editor/arduino/src/hal/'
        destination = 'editor/arduino/src/arduino.cpp'

    shutil.copyfile(source_path + source_file, destination)

    # Generate Pin Array Sizes defines
    # We need to write the hal specific pin size defines on the global defines.h so that it is
    # available everywhere

    if os_platform.system() == 'Windows':
        define_path = 'editor\\arduino\\examples\\Baremetal\\'
    else:
        define_path = 'editor/arduino/examples/Baremetal/'
    file = open(define_path+'defines.h', 'r')
    define_file = file.read() + '\n\n//Pin Array Sizes\n'
    hal = open(destination, 'r')
    lines = hal.readlines()
    for line in lines:
        if (line.find('define NUM_DISCRETE_INPUT') > 0):
            define_file += line
        if (line.find('define NUM_ANALOG_INPUT') > 0):
            define_file += line
        if (line.find('define NUM_DISCRETE_OUTPUT') > 0):
            define_file += line
        if (line.find('define NUM_ANALOG_OUTPUT') > 0):
            define_file += line

    # Write defines.h file back to disk
    if os_platform.system() == 'Windows':
        define_path = 'editor\\arduino\\examples\\Baremetal\\'
    else:
        define_path = 'editor/arduino/examples/Baremetal/'
    f = open(define_path+'defines.h', 'w')
    f.write(define_file)
    f.flush()
    f.close()

    # Generate .elf file
    append_compiler_log(send_text, _('Generating binary file...') + '\n')

    extraflags = ''
    if core == 'esp32:esp32':
        extraflags = ' -MMD -c'

    build_command = cli_command + ['compile', '-v']

    if build_option >= BuildCacheOption.CLEAN_BUILD:
        build_command.append('--clean')

    build_command.extend(['--libraries=editor/arduino', '--build-property', 'compiler.c.extra_flags=-Ieditor/arduino/src/lib' + extraflags])
    build_command.extend(['--build-property', 'compiler.cpp.extra_flags=-Ieditor/arduino/src/lib' + extraflags])
    build_command.extend(['--export-binaries', '-b', platform, 'editor/arduino/examples/Baremetal/Baremetal.ino'])

    return_code = runCommandToWin(send_text, build_command)

    if (return_code != 0):
        append_compiler_log(send_text, '\n' + _('COMPILATION FAILED!') + '\n')

    if (return_code == 0):
        if (port != None):
            append_compiler_log(send_text, '\n' + _('Uploading program to Arduino board at {port}...').format(port=port) + '\n')

            return_code = runCommandToWin(send_text, cli_command + ['upload', '--port',
                                            port, '--fqbn', platform, 'editor/arduino/examples/Baremetal/'])

            append_compiler_log(send_text, '\n' + _('Done!') + '\n')
        else:
            cwd = os.getcwd()
            append_compiler_log(send_text, '\n' + _('OUTPUT DIRECTORY:') + '\n')
            if os_platform.system() == 'Windows':
                append_compiler_log(send_text, cwd + '\\editor\\arduino\\examples\\Baremetal\\build\n')
            else:
                append_compiler_log(send_text, cwd + '/editor/arduino/examples/Baremetal/build\n')
            append_compiler_log(send_text, '\n' + _('COMPILATION DONE!'))

    time.sleep(1)  # make sure files are not in use anymore

    # no clean up
    return

    # Clean up and return
    if os.path.exists(base_path+'POUS.c'):
        os.remove(base_path+'POUS.c')
    if os.path.exists(base_path+'POUS.h'):
        os.remove(base_path+'POUS.h')
    if os.path.exists(base_path+'LOCATED_VARIABLES.h'):
        os.remove(base_path+'LOCATED_VARIABLES.h')
    if os.path.exists(base_path+'VARIABLES.csv'):
        os.remove(base_path+'VARIABLES.csv')
    if os.path.exists(base_path+'Config0.c'):
        os.remove(base_path+'Config0.c')
    if os.path.exists(base_path+'Config0.h'):
        os.remove(base_path+'Config0.h')
    if os.path.exists(base_path+'Config0.o'):
        os.remove(base_path+'Config0.o')
    if os.path.exists(base_path+'Res0.c'):
        os.remove(base_path+'Res0.c')
    if os.path.exists(base_path+'Res0.o'):
        os.remove(base_path+'Res0.o')
    if os.path.exists(base_path+'glueVars.c'):
        os.remove(base_path+'glueVars.c')
