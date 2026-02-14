# -*- coding: utf-8 -*-
"""
MCP 配置管理模块
"""
import json
import os
from pathlib import Path
from src.core.logger import setup_logger

logger = setup_logger('mcp_manager', 'data/logs/mcp_manager.log')

class MCPManager:
    """MCP 配置管理器"""

    def __init__(self):
        # 获取项目根目录
        self.project_root = Path(__file__).parent.parent.parent
        self.config_file = self.project_root / "config" / "mcp.json"
        self.mcps_dir = self.project_root / "mcps"

    def load_config(self):
        """加载 MCP 配置"""
        try:
            if self.config_file.exists():
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 返回默认配置
                logger.warning(f"配置文件不存在: {self.config_file}")
                return {"mcpServers": {}}
        except Exception as e:
            logger.error(f"加载 MCP 配置失败: {e}")
            return {"mcpServers": {}}

    def save_config(self, config):
        """保存 MCP 配置"""
        try:
            # 确保配置目录存在
            self.config_file.parent.mkdir(parents=True, exist_ok=True)

            with open(self.config_file, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            logger.info("MCP 配置已保存")
            return True
        except Exception as e:
            logger.error(f"保存 MCP 配置失败: {e}")
            return False

    def get_all_mcps(self):
        """获取所有 MCP 配置"""
        config = self.load_config()
        servers = config.get('mcpServers', {})

        # 转换为列表格式，方便前端展示
        mcp_list = []
        for name, server_config in servers.items():
            mcp_list.append({
                'name': name,
                'command': server_config.get('command', ''),
                'args': server_config.get('args', []),
                'env': server_config.get('env', {}),
                'enabled': True  # 默认启用
            })

        return mcp_list

    def add_mcp(self, name, command, args, env=None):
        """添加 MCP 配置"""
        try:
            config = self.load_config()

            if name in config['mcpServers']:
                return {"success": False, "error": "MCP 名称已存在"}

            config['mcpServers'][name] = {
                'command': command,
                'args': args if isinstance(args, list) else [args]
            }

            if env:
                config['mcpServers'][name]['env'] = env

            if self.save_config(config):
                logger.info(f"添加 MCP 成功: {name}")
                return {"success": True}
            else:
                return {"success": False, "error": "保存配置失败"}
        except Exception as e:
            logger.error(f"添加 MCP 失败: {e}")
            return {"success": False, "error": str(e)}

    def update_mcp(self, name, command, args, env=None):
        """更新 MCP 配置"""
        try:
            config = self.load_config()

            if name not in config['mcpServers']:
                return {"success": False, "error": "MCP 不存在"}

            config['mcpServers'][name] = {
                'command': command,
                'args': args if isinstance(args, list) else [args]
            }

            if env:
                config['mcpServers'][name]['env'] = env

            if self.save_config(config):
                logger.info(f"更新 MCP 成功: {name}")
                return {"success": True}
            else:
                return {"success": False, "error": "保存配置失败"}
        except Exception as e:
            logger.error(f"更新 MCP 失败: {e}")
            return {"success": False, "error": str(e)}

    def delete_mcp(self, name):
        """删除 MCP 配置"""
        try:
            config = self.load_config()

            if name not in config['mcpServers']:
                return {"success": False, "error": "MCP 不存在"}

            del config['mcpServers'][name]

            if self.save_config(config):
                logger.info(f"删除 MCP 成功: {name}")
                return {"success": True}
            else:
                return {"success": False, "error": "保存配置失败"}
        except Exception as e:
            logger.error(f"删除 MCP 失败: {e}")
            return {"success": False, "error": str(e)}

    def scan_local_mcps(self):
        """扫描本地 MCPs 目录，发现可用的 MCP"""
        try:
            if not self.mcps_dir.exists():
                logger.warning(f"MCPs 目录不存在: {self.mcps_dir}")
                return []

            discovered_mcps = []

            for item in self.mcps_dir.iterdir():
                if not item.is_dir():
                    continue

                # 查找 *_server.py 文件
                server_files = list(item.glob('*_server.py'))
                if server_files:
                    server_file = server_files[0]

                    # 生成 MCP 名称（转换为小写，用连字符分隔）
                    mcp_name = item.name.replace('MCP', '').lower()
                    # 将驼峰命名转换为连字符分隔
                    import re
                    mcp_name = re.sub(r'(?<!^)(?=[A-Z])', '-', item.name.replace('MCP', '')).lower()

                    # 使用相对于项目根目录的路径
                    relative_path = f"mcps/{item.name}/{server_file.name}"

                    discovered_mcps.append({
                        'name': mcp_name,
                        'display_name': item.name,
                        'path': relative_path,
                        'command': 'python',
                        'args': [relative_path]
                    })

            logger.info(f"扫描到 {len(discovered_mcps)} 个 MCP 服务器")
            return discovered_mcps
        except Exception as e:
            logger.error(f"扫描本地 MCPs 失败: {e}")
            return []

    def get_mcp_info(self, name):
        """获取单个 MCP 的详细信息"""
        config = self.load_config()
        server_config = config.get('mcpServers', {}).get(name)

        if not server_config:
            return None

        return {
            'name': name,
            'command': server_config.get('command', ''),
            'args': server_config.get('args', []),
            'env': server_config.get('env', {})
        }
