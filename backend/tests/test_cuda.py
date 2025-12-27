import torch
import time

# 1. 检查 CUDA 环境
print("="*40)
print(f"PyTorch 版本: {torch.__version__}")
print("CUDA 是否可用:", torch.cuda.is_available())

if torch.cuda.is_available():
    print(f"GPU 数量: {torch.cuda.device_count()}")
    print(f"当前 GPU 索引: {torch.cuda.current_device()}")
    print(f"当前 GPU 名称: {torch.cuda.get_device_name(torch.cuda.current_device())}")
print("="*40)

# 2. 设置矩阵大小
N = 4000
print(f"准备创建两个 {N}x{N} 的随机矩阵...")

# 在 CPU 进行矩阵相乘测试
a_cpu = torch.rand(N, N)
b_cpu = torch.rand(N, N)

print("开始 CPU 计算...")
start_time = time.time()
result_cpu = torch.mm(a_cpu, b_cpu)
cpu_time = time.time() - start_time
print(f"CPU 计算时间: {cpu_time:.4f} 秒")

# 如果 CUDA 可用，在 GPU 进行矩阵相乘测试
if torch.cuda.is_available():
    device = torch.device("cuda")

    # 将数据移动到 GPU
    a_gpu = a_cpu.to(device)
    b_gpu = b_cpu.to(device)

    print("开始 GPU 计算...")
    torch.cuda.synchronize()  # 确保计时准确
    start_time = time.time()
    result_gpu = torch.mm(a_gpu, b_gpu)
    torch.cuda.synchronize()
    gpu_time = time.time() - start_time
    print(f"GPU 计算时间: {gpu_time:.4f} 秒")

    # 3. 验证结果正确性
    max_diff = torch.max(torch.abs(result_cpu - result_gpu.cpu())).item()
    print(f"CPU 与 GPU 结果最大差值: {max_diff:e}")
else:
    print("⚠️ 未检测到 CUDA，跳过 GPU 测试。")

print("="*40)
print("测试完成 ✅")
