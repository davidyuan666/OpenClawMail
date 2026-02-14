# -*- coding: utf-8 -*-
"""
CC Switch Manager - 管理 Claude Code 配置切换
"""
import json
from pathlib import Path
from src.core.logger import setup_logger

logger = setup_logger('cc_switch_manager', 'data/logs/cc_switch_manager.log')

CONFIG_FILE = Path.home() / ".cc-switch-config.json"
CLAUDE_SETTINGS = Path.home() / ".claude" / "settings.json"

class CCSwitchManager:
    def __init__(self):
        pass

    def load_configs(self):
        """加载配置"""
        if not CONFIG_FILE.exists():
            return {"profiles": {}, "current": None}
        try:
            with open(CONFIG_FILE) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载配置失败: {e}")
            return {"profiles": {}, "current": None}

    def save_configs(self, data):
        """保存配置"""
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存配置失败: {e}")
            return False

    def load_claude_settings(self):
        """加载 Claude 设置"""
        if not CLAUDE_SETTINGS.exists():
            return {"env": {}, "permissions": {"allow": [], "deny": []}}
        try:
            with open(CLAUDE_SETTINGS) as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"加载 Claude 设置失败: {e}")
            return {"env": {}, "permissions": {"allow": [], "deny": []}}

    def save_claude_settings(self, data):
        """保存 Claude 设置"""
        try:
            CLAUDE_SETTINGS.parent.mkdir(parents=True, exist_ok=True)
            with open(CLAUDE_SETTINGS, 'w') as f:
                json.dump(data, f, indent=2)
            return True
        except Exception as e:
            logger.error(f"保存 Claude 设置失败: {e}")
            return False

    def get_all_profiles(self):
        """获取所有配置"""
        data = self.load_configs()
        profiles = []
        for name, config in data["profiles"].items():
            profiles.append({
                "name": name,
                "base_url": config.get("base_url", ""),
                "auth_token": config.get("auth_token", ""),
                "is_current": name == data.get("current")
            })
        return profiles

    def get_current_profile(self):
        """获取当前配置"""
        data = self.load_configs()
        current = data.get("current")
        if current and current in data["profiles"]:
            profile = data["profiles"][current]
            return {
                "name": current,
                "base_url": profile.get("base_url", ""),
                "auth_token": profile.get("auth_token", "")
            }
        return None

    def add_profile(self, name, base_url, auth_token):
        """添加配置"""
        try:
            data = self.load_configs()
            data["profiles"][name] = {
                "base_url": base_url,
                "auth_token": auth_token
            }
            if self.save_configs(data):
                logger.info(f"添加配置成功: {name}")
                return {"success": True, "message": f"配置 {name} 添加成功"}
            return {"success": False, "error": "保存配置失败"}
        except Exception as e:
            logger.error(f"添加配置失败: {e}")
            return {"success": False, "error": str(e)}

    def update_profile(self, name, base_url, auth_token):
        """更新配置"""
        try:
            data = self.load_configs()
            if name not in data["profiles"]:
                return {"success": False, "error": "配置不存在"}

            data["profiles"][name] = {
                "base_url": base_url,
                "auth_token": auth_token
            }
            if self.save_configs(data):
                logger.info(f"更新配置成功: {name}")
                return {"success": True, "message": f"配置 {name} 更新成功"}
            return {"success": False, "error": "保存配置失败"}
        except Exception as e:
            logger.error(f"更新配置失败: {e}")
            return {"success": False, "error": str(e)}

    def delete_profile(self, name):
        """删除配置"""
        try:
            data = self.load_configs()
            if name not in data["profiles"]:
                return {"success": False, "error": "配置不存在"}

            del data["profiles"][name]
            if data["current"] == name:
                data["current"] = None

            if self.save_configs(data):
                logger.info(f"删除配置成功: {name}")
                return {"success": True, "message": f"配置 {name} 删除成功"}
            return {"success": False, "error": "保存配置失败"}
        except Exception as e:
            logger.error(f"删除配置失败: {e}")
            return {"success": False, "error": str(e)}

    def switch_profile(self, name):
        """切换配置"""
        try:
            data = self.load_configs()
            if name not in data["profiles"]:
                return {"success": False, "error": "配置不存在"}

            profile = data["profiles"][name]
            settings = self.load_claude_settings()
            settings["env"]["ANTHROPIC_BASE_URL"] = profile["base_url"]
            settings["env"]["ANTHROPIC_AUTH_TOKEN"] = profile["auth_token"]
            settings["env"]["CLAUDE_CODE_DISABLE_NONESSENTIAL_TRAFFIC"] = 1

            if not self.save_claude_settings(settings):
                return {"success": False, "error": "保存 Claude 设置失败"}

            data["current"] = name
            if self.save_configs(data):
                logger.info(f"切换配置成功: {name}")
                return {"success": True, "message": f"已切换到配置 {name}"}
            return {"success": False, "error": "保存配置失败"}
        except Exception as e:
            logger.error(f"切换配置失败: {e}")
            return {"success": False, "error": str(e)}
