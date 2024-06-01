from mininet.net import Mininet
from mininet.node import Node
from mininet.node import RemoteController, OVSKernelSwitch
from mininet.link import TCLink
from mininet.cli import CLI

class CustomRouter(Node):
    def config(self, **params):
        super(CustomRouter, self).config(**params)

    def terminate(self):
        super(CustomRouter, self).terminate()

def calcular_direcciones():
    enlaces_wan = {}
    direcciones_privadas = {}

    for num_sucursal in range(1, 7):
        enlaces_wan[f"suc{num_sucursal}"] = f"192.168.100.{(num_sucursal - 1) * 8}/29"
        direcciones_privadas[f"suc{num_sucursal}"] = f"10.0.{num_sucursal}.0/24"

    return enlaces_wan, direcciones_privadas

def crear_topologia(enlaces_wan, direcciones_privadas):
    net = Mininet(switch=OVSKernelSwitch, link=TCLink)

    net.addController('c', controller=RemoteController, ip='127.0.0.1', port=6653)

    r_central = net.addHost('rCent')

    for num_sucursal in range(1, 7):
        sucursal = f"suc{num_sucursal}"
        dir_wan = enlaces_wan[sucursal]

        ip_router_wan = f"192.168.100.{(num_sucursal - 1) * 8 + 1}/29"
        ip_central_wan = f"192.168.100.{(num_sucursal - 1) * 8 + 2}/29"
        ip_router_lan = f"10.0.{num_sucursal}.1/24"
        ip_puesto1_lan = f"10.0.{num_sucursal}.2/24"
        ip_puesto2_lan = f"10.0.{num_sucursal}.3/24"

        r_sucursal = net.addHost(f'router{sucursal}', cls=CustomRouter, ip=ip_router_lan)

        p1 = net.addHost(f'p1{sucursal}', ip=ip_puesto1_lan)
        p2 = net.addHost(f'p2{sucursal}', ip=ip_puesto2_lan)

        sw_wan = net.addSwitch(f'swWAN{sucursal}')
        sw_lan = net.addSwitch(f'swLAN{sucursal}')

        net.addLink(r_central, sw_wan)
        r_central.cmd(f'ifconfig {r_central.name}-{num_sucursal - 1} {ip_central_wan}')

        net.addLink(r_sucursal, sw_wan)
        r_sucursal.cmd(f'ifconfig {r_sucursal.name} {ip_router_wan}')

        net.addLink(r_sucursal, sw_lan)
        net.addLink(p1, sw_lan)
        net.addLink(p2, sw_lan)

        r_sucursal.cmd(f'ip route add 192.168.100.0/24 via {ip_central_wan}')
        r_central.cmd(f'ip route add {direcciones_privadas[sucursal]} via {ip_router_wan}')

    net.build()
    net.start()
    CLI(net)
    net.stop()

if __name__ == '__main__':
    enlaces_wan, direcciones_privadas = calcular_direcciones()
    crear_topologia(enlaces_wan, direcciones_privadas)
