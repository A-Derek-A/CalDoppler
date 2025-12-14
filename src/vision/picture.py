import matplotlib

# 在导入pyplot之前设置非交互式后端
# matplotlib.use("Agg")  # 不显示图形，只保存到文件
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from scipy.interpolate import griddata


def plot_footprint(
    data: list[tuple[float, float, float]],
    save_dir: Path,
    filename: str = "footprint"
):
    """将3D图保存到文件，而不是显示"""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    x = [p[0] for p in data]
    y = [p[1] for p in data]
    z = [p[2] for p in data]

    scatter = ax.scatter(x, y, z, c=z, cmap="viridis", s=20, alpha=0.8)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("3D Plot")

    plt.colorbar(scatter, ax=ax, label="Z value")
    plt.tight_layout()
    
    # 保存到文件而不是显示
    plt.savefig(save_dir / filename, dpi=300, bbox_inches="tight")
    
    print(f"图形已保存到: {save_dir / filename}")
    plt.show()
    plt.close(fig)  # 关闭图形释放内存

def plot_contour_irregular(
    data: list[tuple[float, float, float]],
    saved_dir: Path, # 当前代码未使用
    filename: str = "contour.png",
):
    if not data or len(data[0]) < 3:
         print("Invalid data format.")
         return

    # 分别提取 x, y, z
    points = np.array([(p[0], p[1]) for p in data])
    values = np.array([p[2] for p in data])

    # 定义插值的目标网格
    xi = np.linspace(points[:, 0].min(), points[:, 0].max(), 100)
    yi = np.linspace(points[:, 1].min(), points[:, 1].max(), 100)
    Xi, Yi = np.meshgrid(xi, yi)

    # 进行插值 ('linear', 'nearest', 'cubic')
    Zi = griddata(points, values, (Xi, Yi), method='linear')

    # 绘制等高线图
    plt.figure(figsize=(6, 4))
    if Zi is not None and not np.all(np.isnan(Zi)): # 检查插值是否成功
        cs = plt.contour(Xi, Yi, Zi, levels=70, colors="k")
        plt.clabel(cs, inline=True, fontsize=8)
    else:
       print("Interpolation failed or resulted in no valid data.")

    plt.title("Contour plot: doppler (interpolated)")
    plt.xlabel("x")
    plt.ylabel("y")
    plt.grid(True)

    plt.savefig(saved_dir / filename)
    
    plt.show()
    plt.close()


def save_3d_plot_to_file(
    data: list[tuple[float, float, float]],
    saved_dir: Path,
    filename: str = "output.png",
):
    """将3D图保存到文件，而不是显示"""
    fig = plt.figure(figsize=(10, 8))
    ax = fig.add_subplot(111, projection="3d")

    x = [p[0] for p in data]
    y = [p[1] for p in data]
    z = [p[2] for p in data]

    scatter = ax.scatter(x, y, z, c=z, cmap="viridis", s=20, alpha=0.8)

    ax.set_xlabel("X")
    ax.set_ylabel("Y")
    ax.set_zlabel("Z")
    ax.set_title("3D Plot")

    plt.colorbar(scatter, ax=ax, label="Z value")
    plt.tight_layout()
    
    # 保存到文件而不是显示
    plt.savefig(saved_dir / filename, dpi=300, bbox_inches="tight")
    
    print(f"图形已保存到: {saved_dir / filename}")
    plt.show()
    plt.close(fig)  # 关闭图形释放内存


# def draw_picture(
#     points: list[tuple[float,float, float]],
#     save_path: Path,
#     is_saved: bool
# ):

#     """
#     绘制三维散点图
#     data: list[tuple[float, float, float]] 三维坐标点列表
#     """
#     # 分离x, y, z坐标
#     x_coords = [point[0] for point in points]
#     y_coords = [point[1] for point in points]
#     z_coords = [point[2] for point in points]

#     # 创建3D图形
#     fig = plt.figure(figsize=(10, 8))
#     ax = fig.add_subplot(111, projection='3d')

#     # 绘制散点
#     scatter = ax.scatter(x_coords, y_coords, z_coords,
#                         c=z_coords,  # 根据z值设置颜色
#                         cmap='viridis',  # 颜色映射
#                         s=50,  # 点的大小
#                         alpha=0.8,  # 透明度
#                         edgecolors='k',  # 边缘颜色
#                         linewidth=0.5)  # 边缘线宽

#     # 设置坐标轴标签
#     ax.set_xlabel('lat', fontsize=12)
#     ax.set_ylabel('lon', fontsize=12)
#     ax.set_zlabel('doppler shift', fontsize=12)

#     # 设置标题
#     ax.set_title('doppler shift', fontsize=14, pad=20)

#     # 添加颜色条
#     plt.colorbar(scatter, ax=ax, shrink=0.5, aspect=5, label='doppler shift')

#     # 调整视角
#     ax.view_init(elev=20, azim=45)

#     # 设置网格
#     ax.grid(True, alpha=0.3)

#     plt.tight_layout()
#     # plt.show()
#     if is_saved:
#         plt.savefig(save_path)
