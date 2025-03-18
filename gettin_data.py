import glob, sys, time, serial, os
from brainflow.board_shim import BoardShim, BrainFlowInputParams
from serial import Serial
from threading import Thread, Event
from queue import Queue
from psychopy.hardware import keyboard
import numpy as np

# 🎯 Settings
lsl_out = False
save_dir = f'data/misc/'  # Directory to save data
run = 1  # Run number for trial sequence
save_file_aux = save_dir + f'aux_run-{run}.npy'
save_file_eeg = save_dir + f'eeg_run-{run}.npy'  # ✅ Added EEG file

sampling_rate = 250
CYTON_BOARD_ID = 0  # 0 = No Daisy, 2 = Daisy, 6 = WiFi shield
BAUD_RATE = 115200
ANALOGUE_MODE = '/2'  # Reads from A5(D11), A6(D12), A7(D13) if no WiFi

# 🔍 Find OpenBCI Port
def find_openbci_port():
    """Finds the port to which the Cyton Dongle is connected."""
    if sys.platform.startswith('win'):
        ports = ['COM%s' % (i + 1) for i in range(256)]
    elif sys.platform.startswith('linux') or sys.platform.startswith('cygwin'):
        ports = glob.glob('/dev/ttyUSB*')
    elif sys.platform.startswith('darwin'):
        ports = glob.glob('/dev/cu.usbserial*')
    else:
        raise EnvironmentError('Error finding ports on your operating system')

    for port in ports:
        try:
            s = Serial(port=port, baudrate=BAUD_RATE, timeout=None)
            s.write(b'v')
            time.sleep(2)
            if s.inWaiting():
                line = ''
                while '$$$' not in line:
                    line += s.read().decode('utf-8', errors='replace')
                if 'OpenBCI' in line:
                    return port
            s.close()
        except (OSError, serial.SerialException):
            pass

    raise OSError('Cannot find OpenBCI port.')

# 🎯 Setup BrainFlow
params = BrainFlowInputParams()
params.serial_port = find_openbci_port()
board = BoardShim(CYTON_BOARD_ID, params)
board.prepare_session()
board.start_stream(45000)
stop_event = Event()

# 🧠 Data Collection Thread
def get_data(queue_in, lsl_out=False):
    while not stop_event.is_set():
        data_in = board.get_board_data()
        eeg_in = data_in[board.get_eeg_channels(CYTON_BOARD_ID)]
        aux_in = data_in[board.get_analog_channels(CYTON_BOARD_ID)]
        timestamp_in = data_in[board.get_timestamp_channel(CYTON_BOARD_ID)]

        if len(timestamp_in) > 0:
            queue_in.put((eeg_in, aux_in, timestamp_in))

        time.sleep(0.1)

# Start EEG Data Thread
queue_in = Queue()
cyton_thread = Thread(target=get_data, args=(queue_in, lsl_out))
cyton_thread.daemon = True
cyton_thread.start()

# ⌨️ Keyboard Input
kb = keyboard.Keyboard()
eeg = np.zeros((8, 0))
aux = np.zeros((3, 0))

# 🏃 Main Loop
while not stop_event.is_set():
    time.sleep(0.1)
    keys = kb.getKeys(['escape'], waitRelease=False)  # ✅ Non-blocking keyboard check
    if 'escape' in keys:
        stop_event.set()
        break

    while not queue_in.empty():
        eeg_in, aux_in, timestamp_in = queue_in.get()
        eeg = np.hstack((eeg, eeg_in))
        aux = np.hstack((aux, aux_in))

# 💾 Save EEG & Aux Data
os.makedirs(save_dir, exist_ok=True)
np.save(save_file_aux, aux)
np.save(save_file_eeg, eeg)  # ✅ Save EEG data

# 🚀 Cleanup
stop_event.set()
board.stop_stream()
board.release_session()  # ✅ Ensure session is properly released
