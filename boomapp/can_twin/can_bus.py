import can
import threading
import time
from queue import Queue

class CANBusSimulator:
    def __init__(self, channel='vcan0', bustype='virtual'):
        self.channel = channel
        self.bustype = bustype
        self.bus = None
        self.running = False
        self.rx_queue = Queue()
        self.tx_queue = Queue()
    
    def start(self):
        try:
            self.bus = can.interface.Bus(channel=self.channel, bustype=self.bustype)
            self.running = True
            threading.Thread(target=self._receive_loop, daemon=True).start()
            threading.Thread(target=self._transmit_loop, daemon=True).start()
        except Exception as e:
            print(f"CAN bus virtual mode: {e}")
            self.running = True
    
    def _receive_loop(self):
        while self.running:
            if self.bus:
                msg = self.bus.recv(timeout=0.1)
                if msg:
                    self.rx_queue.put(msg)
    
    def _transmit_loop(self):
        while self.running:
            if not self.tx_queue.empty():
                msg = self.tx_queue.get()
                if self.bus:
                    self.bus.send(msg)
            time.sleep(0.01)
    
    def send_message(self, arbitration_id, data):
        msg = can.Message(arbitration_id=arbitration_id, data=data, is_extended_id=False)
        self.tx_queue.put(msg)
    
    def receive_message(self):
        if not self.rx_queue.empty():
            return self.rx_queue.get()
        return None
    
    def stop(self):
        self.running = False
        if self.bus:
            self.bus.shutdown()
