# Reliable Data Transfer over UDP

For CS456 University of Waterloo  
Implements and simulates a unidirectional reliable data transfer over UDP. It successfully transfers a text file from one host to another even in a simulated unreliable network. It deals with packet loss, orders packet correctly, and utilizes duplicate packets.  
You'll need to download Python 3   
To run:  
The network emulator requires Python 3. You can use the emulator either by executing the provided nEmulator script or by running `python3 network_emulator.py` directly.  
Find usage instructions using ./nEmulator -h  
The sender requires Python 3. You can use it by running `python3 sender.py <emulator_host> <emulator_port> <sender_port> <timeout_int> <filename>` directly.  
The receiver requires Python 3. You can use it by running `python3 receiver.py <emulator_host> <emulator_port> <receiver_port> <filename>` directly.  
