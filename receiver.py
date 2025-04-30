from socket import *
import sys
from packet import Packet

def receiver(emulator_host, emulator_port, receiver_port, filename):
  # Setup sockets
  receiver_socket = socket(AF_INET, SOCK_DGRAM)
  try:
    receiver_socket.bind(("", receiver_port))
  except OSError:
    receiver_socket.close()
    print("Unavaible port number")
    return 

  expected_seqnum = 0
  buffer = {}

  # Write to logs
  with open(filename, "w") as output, open("arrival.log", "w") as arrival_log:
    while True:
      # Receive packets
      packet = receiver_socket.recvfrom(1024)[0]
      packet_type, seqnum, _, data = Packet.decode(Packet(packet))

      if packet_type == 2: # EOT packet received
        arrival_log.write("EOT\n")
        eot_packet = Packet.encode(Packet(2, seqnum, 0, ""))
        receiver_socket.sendto(eot_packet, (emulator_host, emulator_port))
        break

      arrival_log.write(f"{seqnum}\n")
      # Send ACK for received packet
      ack_packet = Packet.encode(Packet(0, seqnum, 0, ""))
      receiver_socket.sendto(ack_packet, (emulator_host, emulator_port))

      # Buffer packets
      if seqnum >= expected_seqnum:
        buffer[seqnum] = data

      # Write to file consecutively if expected packet arrives
      while expected_seqnum in buffer:
        output.write(buffer[expected_seqnum])
        del buffer[expected_seqnum]
        expected_seqnum += 1

  receiver_socket.close()

if __name__ == "__main__":
  if len(sys.argv) != 5 or (int(sys.argv[2]) < 1024 or int(sys.argv[2]) > 65535) or (int(sys.argv[3]) < 1024 or int(sys.argv[3]) > 65535):
    print("Error: Invalid Arguments, try python receiver.py <emulator_host> <emulator_port> <receiver_port> <filename>")
    sys.exit(1)
  receiver(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), sys.argv[4])