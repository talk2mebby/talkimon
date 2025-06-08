from zeroconf import ServiceBrowser, Zeroconf, ServiceInfo
import socket
import threading

SERVICE_TYPE = "_meshnode._tcp.local."

def start_advertising(node_id, port):
    zeroconf = Zeroconf()
    ip = socket.gethostbyname(socket.gethostname())
    service_info = ServiceInfo(
        SERVICE_TYPE,
        f"{node_id}.{SERVICE_TYPE}",
        addresses=[socket.inet_aton(ip)],
        port=port,
        properties={}
    )
    zeroconf.register_service(service_info)
    print(f"[MeshNode] Advertising as {node_id} on {ip}:{port}")

def start_discovery(on_peer_found):
    class PeerListener:
        def add_service(self, zeroconf, type, name):
            info = zeroconf.get_service_info(type, name)
            if info:
                ip = socket.inet_ntoa(info.addresses[0])
                port = info.port
                peer_url = f"http://{ip}:{port}"
                on_peer_found(peer_url)

    zeroconf = Zeroconf()
    ServiceBrowser(zeroconf, SERVICE_TYPE, PeerListener())
    print("[MeshNode] Peer discovery started...")
    threading.Event().wait()
