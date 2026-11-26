# ============================================================
# PLACEHOLDER — Generate file ini dari .proto lo sendiri:
#
#   protoc --python_out=proto/ proto/my.proto
#
# Class yang dibutuhkan: GameData
# Fields yang dipake:
#   timestamp, game_name, game_version, version_code,
#   os_info, device_type, network_provider, connection_type,
#   screen_width, screen_height, dpi, cpu_info, total_ram,
#   gpu_name, gpu_version, user_id, ip_address, language,
#   open_id, access_token, platform_type, field_99, field_100,
#   nickname (optional)
# ============================================================
raise ImportError(
    "proto/my_pb2.py adalah placeholder. "
    "Compile dari .proto lo sendiri: "
    "protoc --python_out=proto/ proto/my.proto"
)
