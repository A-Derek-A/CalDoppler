import math
import random
from typing import Tuple


def footprint_central_angle_rad(h_km: float, e0_deg: float, R_km: float = 6371.0) -> float:
    """
    计算卫星覆盖区域的地心角α
    
    参数:
        h_km: 卫星高度 (km)
        e0_deg: 高度截止角/最小仰角 (度)
        R_km: 地球半径 (km)
    
    返回:
        α: 地心角 (弧度)
    """
    # 将角度转换为弧度
    e0_rad = math.radians(e0_deg)
    
    # 计算核心部分: R/(R+H) * cos(E0)
    ratio = (R_km / (R_km + h_km)) * math.cos(e0_rad)
    
    # 确保值在acos的定义域 [-1, 1] 内
    ratio = max(-1.0, min(1.0, ratio))
    
    # 计算最终结果: arccos(...) - E0
    alpha_rad = math.acos(ratio) - e0_rad
    
    return alpha_rad


def footprint_surface_radius_km(h_km: float, R_km: float = 6371.0) -> float:
    """Arc length on Earth's surface from sub-satellite point to horizon."""
    psi = footprint_central_angle_rad(h_km, R_km)
    return R_km * psi


def sample_point_in_spherical_cap(
    center_lat_deg: float,
    center_lon_deg: float,
    cap_angle_rad: float,
    eps: float = 1e-12,
) -> Tuple[float, float]:
    """
    Uniform sampling over a spherical cap.

    Args:
        center_lat_deg: Center latitude in degrees [-90, 90]
        center_lon_deg: Center longitude in degrees [-180, 180]
        cap_angle_rad: Angular radius of the cap in radians [0, π]
        eps: Numerical tolerance

    Returns:
        (latitude_deg, longitude_deg)
    """
    # 边界情况处理
    if cap_angle_rad <= eps:
        return center_lat_deg, center_lon_deg

    if cap_angle_rad >= math.pi - eps:
        # 整个球面均匀采样
        u = random.uniform(-1, 1)
        lat_rad = math.asin(u)
        lon_rad = random.uniform(-math.pi, math.pi)
        return math.degrees(lat_rad), math.degrees(lon_rad)

    # 常规采样
    cos_cap = math.cos(cap_angle_rad)
    u = random.uniform(cos_cap, 1.0)
    theta = math.acos(u)  # 角距离
    phi = random.uniform(0, 2 * math.pi)  # 方位角

    # 转换为弧度
    lat1 = math.radians(center_lat_deg)
    lon1 = math.radians(center_lon_deg)

    # 计算新纬度
    sin_lat2 = math.sin(lat1) * math.cos(theta) + math.cos(lat1) * math.sin(
        theta
    ) * math.cos(phi)
    sin_lat2_clamped = max(-1.0 + eps, min(1.0 - eps, sin_lat2))
    lat2 = math.asin(sin_lat2_clamped)

    # 计算新经度
    y = math.sin(phi) * math.sin(theta) * math.cos(lat1)
    x = math.cos(theta) - math.sin(lat1) * math.sin(lat2)

    # 避免除零
    if abs(x) < eps and abs(y) < eps:
        delta_lon = 0.0
    else:
        delta_lon = math.atan2(y, x)

    lon2 = lon1 + delta_lon

    # 规范化到 [-π, π]
    lon2 = (lon2 + math.pi) % (2 * math.pi) - math.pi

    # 返回度数
    lat_deg = math.degrees(lat2)
    lon_deg = math.degrees(lon2)

    return lat_deg, lon_deg
