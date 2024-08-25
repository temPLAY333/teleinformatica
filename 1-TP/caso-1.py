from mininet.net import Mininet
from mininet.node import Node, OVSKernelSwitch
from mininet.cli import CLI

# Alumno: Tomás Bourguet
# Legajo: 61235
# Caso: 1

class Mi_router_linux(Node):
    def config(self, **params):
        super(Mi_router_linux, self).config(**params)
        self.cmd('sysctl net.ipv4.ip_forward=1')

    def terminate(self):
        super(Mi_router_linux, self).terminate()

def configurar_router(central_router, sucursal_router, num_sucursal):
    ip_central_wan = f'192.168.100.{6 + (8 * (num_sucursal - 1))}/29'
    ip_sucursal_wan = f'192.168.100.{1 + (8 * (num_sucursal - 1))}/29'

    central_router.cmd(f'ifconfig {central_router.name}-eth{num_sucursal - 1} {ip_central_wan}')
    central_router.cmd(f'ip route add 10.0.{num_sucursal}.0/24 via {ip_sucursal_wan.split("/")[0]}')

    sucursal_router.cmd(f'ifconfig {sucursal_router.name}-eth1 {ip_sucursal_wan}')
    sucursal_router.cmd(f'ip route add 10.0.0.0/8 via {ip_central_wan.split("/")[0]}')
    sucursal_router.cmd(f'ip route add 192.168.100.0/24 via {ip_central_wan.split("/")[0]}')

def configurar_host(host, num_sucursal):
    host.cmd(f'ip route add default via 10.0.{num_sucursal}.1')

def crear_red():
    net = Mininet(switch=OVSKernelSwitch, build=False)

    central_router = net.addHost('rc', cls=Mi_router_linux, ip='192.168.100.6/29')

    for num_sucursal in range(1, 7):
        sw_wan = net.addSwitch(f'swWAN{num_sucursal}', cls=OVSKernelSwitch, failMode='standalone')
        net.addLink(central_router, sw_wan)

        sucursal_router = net.addHost(f'rSuc{num_sucursal}', cls=Mi_router_linux, ip=f'10.0.{num_sucursal}.1/24')
        sw_lan = net.addSwitch(f'swLAN{num_sucursal}', cls=OVSKernelSwitch, failMode='standalone')
        net.addLink(sucursal_router, sw_lan)
        net.addLink(sucursal_router, sw_wan)

        for host_num in range(1, 3):
            host = net.addHost(f'h{host_num}Suc{num_sucursal}', ip=f'10.0.{num_sucursal}.{host_num + 1}/24')
            net.addLink(host, sw_lan)

    net.build()

    for switch in net.switches:
        switch.start([])

    for num_sucursal in range(1, 7):
        sucursal_router = net.get(f'rSuc{num_sucursal}')
        configurar_router(central_router, sucursal_router, num_sucursal)
        for host_num in range(1, 3):
            host = net.get(f'h{host_num}Suc{num_sucursal}')
            configurar_host(host, num_sucursal)

    CLI(net)
    net.stop()

if __name__ == '__main__':
    crear_red()