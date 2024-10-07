from m5.objects import *

# Root configuration
root = Root(full_system=False)

# Set up a basic system
system = System()

# x86 system architecture
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '2GHz'
system.clk_domain.voltage_domain = VoltageDomain()

system.mem_mode = 'timing'  # Set memory mode
system.mem_ranges = [AddrRange('512MB')]  # Memory size

# Set up the CPU
system.cpu = TimingSimpleCPU()

# Add interrupt controllers for each CPU thread (x86-specific)
system.cpu.createInterruptController()

# Set up the L1 instruction and data caches
cache_size = '16kB'
class L1ICache(Cache):
    size = cache_size
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20
    # prefetcher = StridePrefetcher()

class L1DCache(Cache):
    size = cache_size
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20
    # prefetcher = StridePrefetcher()

# Set up the CPU's L1 instruction and data caches
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()

# Connect L1 caches to the CPU
system.cpu.icache_port = system.cpu.icache.cpu_side
system.cpu.dcache_port = system.cpu.dcache.cpu_side

# Set up the memory bus (main bus)
system.membus = SystemXBar()

# Connect L1 caches directly to the memory bus
system.cpu.icache.mem_side = system.membus.slave
system.cpu.dcache.mem_side = system.membus.slave

# Set up the memory controller and connect it directly to the memory bus
system.mem_ctrl = SimpleMemory()  # SimpleMemory as the memory controller
system.mem_ctrl.range = system.mem_ranges[0]  # Set the memory range
system.membus.master = system.mem_ctrl.port  # Connect memory controller to memory bus

# Set up an I/O bus for the interrupt controller
system.iobus = IOXBar()

# Connect CPU interrupt ports to the I/O bus
system.cpu.interrupts[0].pio = system.iobus.master
system.cpu.interrupts[0].int_requestor = system.iobus.slave
system.cpu.interrupts[0].int_responder = system.iobus.master

# Bridge to connect the I/O bus to the memory bus
system.iobridge = Bridge()
system.iobridge.slave = system.iobus.master
system.iobridge.master = system.membus.slave
system.iobridge.ranges = [AddrRange('512MB')]  # Limit the I/O bus address range

# Create an I/O Controller
system.system_port = system.membus.slave

# Set up the workload
system.workload = SEWorkload.init_compatible("tests/test-progs/hello/bin/x86/linux/hello")

# Set up the process to run
process = Process()
process.cmd = ['tests/test-progs/hello/bin/x86/linux/hello']
system.cpu.workload = process
system.cpu.createThreads()

# Instantiate system
root.system = system

# Instantiate simulation
m5.instantiate()

# Start simulation
print("Beginning simulation!")
exit_event = m5.simulate()

print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")