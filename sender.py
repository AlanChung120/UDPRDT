from socket import *
import sys
from packet import Packet

WINDOW_SIZE = 10

def sender(emulator_host, emulator_port, sender_port, timeout_int, filename):
  # Setup sockets
  sender_socket = socket(AF_INET, SOCK_DGRAM)
  try:
    sender_socket.bind(("", sender_port))
  except OSError:
    sender_socket.close()
    print("Unavaible port number")
    return 
  sender_socket.settimeout(timeout_int / 1000.0)

  # Split file into chunks
  with open(filename, "r") as file:
    chunks = list(iter(lambda: file.read(500), ""))

  send_base = 0
  next_seqnum = 0
  send_count = 0
  unacked_packets = {}

  # Write to logs
  with open("seqnum.log", "w") as seq_log, open("ack.log", "w") as ack_log:
    while send_base < len(chunks) or len(unacked_packets) > 0:
      # Send packets
      while send_count < WINDOW_SIZE and next_seqnum < len(chunks):
        packet = Packet.encode(Packet(1, next_seqnum, len(chunks[next_seqnum]), chunks[next_seqnum]))
        sender_socket.sendto(packet, (emulator_host, emulator_port))
        send_count += 1
        seq_log.write(f"{next_seqnum}\n")
        unacked_packets[next_seqnum] = packet
        next_seqnum += 1

      # Wait to receive ACKs for the packets
      send_count = 0
      try:
        while True:
          ack_packet = sender_socket.recvfrom(1024)[0]
          ack_type, ack_seqnum, _, _ = Packet.decode(Packet(ack_packet))

          if ack_type == 0:  # ACK packet
            ack_log.write(f"{ack_seqnum}\n")
            if ack_seqnum in unacked_packets:
              del unacked_packets[ack_seqnum]
            if ack_seqnum == send_base:
              while send_base not in unacked_packets and send_base < next_seqnum:
                send_base += 1

      # Retransmit unacked packets because timeout
      except timeout:
        for seq in sorted(unacked_packets):
          sender_socket.sendto(unacked_packets[seq], (emulator_host, emulator_port))
          send_count += 1
          seq_log.write(f"{seq}\n")

    # Send EOT
    eot_packet = Packet.encode(Packet(2, send_base, 0, ""))
    sender_socket.sendto(eot_packet, (emulator_host, emulator_port))
    seq_log.write("EOT\n")

    # Wait to receive EOT ACK
    while True:
      ack_packet = sender_socket.recvfrom(1024)[0]
      ack_type = Packet.decode(Packet(ack_packet))[0]

      if ack_type == 2:  # EOT packet received
        ack_log.write("EOT\n")
        break

  sender_socket.close()

if __name__ == "__main__":
  if len(sys.argv) != 6 or (int(sys.argv[2]) < 1024 or int(sys.argv[2]) > 65535) or (int(sys.argv[3]) < 1024 or int(sys.argv[3]) > 65535):
    print("Error: Invalid Arguments, try python sender.py <emulator_host> <emulator_port> <sender_port> <timeout_int> <filename>")
    sys.exit(1)
  sender(sys.argv[1], int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]), sys.argv[5])