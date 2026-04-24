import psutil

cores = psutil.cpu_count(logical=True)
phys = psutil.cpu_count(logical=False)
usage = psutil.cpu_percent(interval=2, percpu=True)
ram = psutil.virtual_memory()

print(f"CPU Cores: {phys} physical, {cores} logical")
print(f"Per-core: {[f'{u:.0f}%' for u in usage]}")
print(f"Avg CPU: {sum(usage)/len(usage):.1f}%")
print(f"RAM: {ram.used/1024**3:.1f}GB / {ram.total/1024**3:.1f}GB ({ram.percent:.0f}%)")
print(f"Free RAM: {ram.available/1024**3:.1f}GB")
