from m5.objects import *

# Root configuration
root = Root(full_system=False)

# Set up a basic system
system = System()

# System architecture and clock setup
system.clk_domain = SrcClockDomain()
system.clk_domain.clock = '2GHz'
system.clk_domain.voltage_domain = VoltageDomain()
system.mem_mode = 'timing'  # Set memory mode
system.mem_ranges = [AddrRange('512MB')]  # Memory size

# Memory bus configuration
system.membus = SystemXBar()

# Set up the CPU
system.cpu = TimingSimpleCPU()

# Add interrupt controllers for each CPU thread (x86-specific)
system.cpu.createInterruptController()

# Cache size configuration
cache_size = '64kB'
victim_cache_size = '4kB'  # Smaller victim cache

class L1ICache(Cache):
    size = cache_size
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20
    prefetcher = StridePrefetcher()

class L1DCache(Cache):
    size = cache_size
    assoc = 2
    tag_latency = 2
    data_latency = 2
    response_latency = 2
    mshrs = 4
    tgts_per_mshr = 20
    prefetcher = StridePrefetcher()

class VictimCache(Cache):
    size = victim_cache_size
    assoc = 4  # Typically more associative
    tag_latency = 1
    data_latency = 1
    response_latency = 1
    mshrs = 2
    tgts_per_mshr = 12

# Instantiate caches
system.cpu.icache = L1ICache()
system.cpu.dcache = L1DCache()
system.cpu.vcache = VictimCache()

# Connect L1 Instruction Cache
system.cpu.icache.cpu_side = system.cpu.icache_port
system.cpu.icache.mem_side = system.membus.slave

# Connect L1 Data Cache to Victim Cache
system.cpu.dcache.cpu_side = system.cpu.dcache_port
system.cpu.dcache.mem_side = system.cpu.vcache.cpu_side

# Connect Victim Cache to Memory Bus
system.cpu.vcache.mem_side = system.membus.slave

# Memory controller setup
system.mem_ctrl = SimpleMemory()
system.mem_ctrl.range = system.mem_ranges[0]
system.membus.master = system.mem_ctrl.port

# IO setup
system.iobus = IOXBar()
system.cpu.interrupts[0].pio = system.iobus.master
system.cpu.interrupts[0].int_requestor = system.iobus.slave
system.cpu.interrupts[0].int_responder = system.iobus.master

# Bridge between IO and memory bus
system.iobridge = Bridge()
system.iobridge.slave = system.iobus.master
system.iobridge.master = system.membus.slave
system.iobridge.ranges = [AddrRange('512MB')]

# Set up workload and simulation
system.workload = SEWorkload.init_compatible("tests/test-progs/hello/bin/x86/linux/hello")
process = Process()
process.cmd = ['tests/test-progs/hello/bin/x86/linux/hello']
system.cpu.workload = process
system.cpu.createThreads()

# Instantiate system
root.system = system
m5.instantiate()

# Start simulation
print("Beginning simulation!")
exit_event = m5.simulate()
print(f"Exiting @ tick {m5.curTick()} because {exit_event.getCause()}")
