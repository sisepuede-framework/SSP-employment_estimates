import psutil

# Get RAM info
ram = psutil.virtual_memory()
print(f"Total RAM: {ram.total / (1024**3):.2f} GB")
print(f"Available RAM: {ram.available / (1024**3):.2f} GB")
print(f"Used RAM: {ram.used / (1024**3):.2f} GB")
print(f"RAM Usage: {ram.percent}%")
print()

# Estimate memory needed for 960x960 matrix inversion
matrix_size = 960
bytes_per_float = 8  # float64
matrix_memory = (matrix_size ** 2) * bytes_per_float
working_memory = matrix_memory * 5  # Conservative estimate for working space during inversion

print(f"Estimated memory needed for L_BASE calculation:")
print(f"  Matrix size: {matrix_size}x{matrix_size}")
print(f"  Storage: {matrix_memory / (1024**2):.2f} MB")
print(f"  Working memory (conservative): {working_memory / (1024**2):.2f} MB ({working_memory / (1024**3):.2f} GB)")
print()

if ram.available > working_memory:
    print("✓ You have enough available RAM to calculate L_BASE")
else:
    print("✗ WARNING: May not have enough RAM. Close other applications first.")
    print(f"  Need: {working_memory / (1024**3):.2f} GB")
    print(f"  Available: {ram.available / (1024**3):.2f} GB")
    print(f"  Shortfall: {(working_memory - ram.available) / (1024**3):.2f} GB")
