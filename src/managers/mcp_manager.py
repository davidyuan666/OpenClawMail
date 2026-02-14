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

    MCP_CONFIG_FILE = ".mcp.json"
    MCPS_DIR = "C:/workspace/claudecodelabspace/my-mcps"

    def __init__(self):
        self.config_file = self.MCP_CONFIG_FILE

    def load_config(self):
        """加载 MCP 配置"""
        try:
            if os.path.exists(self.config_file):
                with open(self.config_file, 'r', encoding='utf-8') as f:
                    return json.load(f)
            else:
                # 返回默认配置
                return {"mcpServers": {}}
        except Exception as e:
            logger.error(f"加载 MCP 配置失败: {e}")
            return {"mcpServers": {}}

    def save_config(self, config):
        """保存 MCP 配置"""
        try:
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
            if not os.path.exists(self.MCPS_DIR):
                return []

            discovered_mcps = []

            for item in os.listdir(self.MCPS_DIR):
                mcp_path = os.path.join(self.MCPS_DIR, item)
                if not os.path.isdir(mcp_path):
                    continue

                # 查找 *_server.py 文件
                server_files = list(Path(mcp_path).glob('*_server.py'))
                if server_files:
                    server_file = server_files[0]

                    # 生成 MCP 名称（转换为小写，用连字符分隔）
                    mcp_name = item.replace('MCP', '').lower()
                    if not mcp_name.endswith('-'):
                        mcp_name = mcp_name.replace('mcp', '')
                    mcp_name = '-'.join([word for word in mcp_name.split() if word])

                    discovered_mcps.append({
                        'name': mcp_name,
                        'display_name': item,
                        'path': str(server_file).replace('\\', '/'),
                        'command': 'python',
                        'args': [str(server_file).replace('\\', '/')]
                    })

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
