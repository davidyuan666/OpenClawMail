# Video Analyzer MCP Server

视频内容分析 MCP 服务器，支持 Bilibili 和 YouTube 视频分析。

## 功能特性

- 分析单个视频的详细信息（标题、描述、观看量、点赞数等）
- 分析UP主/频道的视频内容，总结主题和统计数据
- 支持 YouTube 和 Bilibili 两大平台

## 安装依赖

```bash
pip install -r requirements.txt
```

## 使用方法

### 工具列表

1. **analyze_video** - 分析单个视频
   - 参数：
     - `url`: 视频链接（支持 YouTube 和 Bilibili）

2. **analyze_channel** - 分析频道/UP主
   - 参数：
     - `url`: 频道/UP主主页链接
     - `max_videos`: 分析的最大视频数量（默认10）

## 支持的URL格式

### YouTube
- https://www.youtube.com/watch?v=VIDEO_ID
- https://youtu.be/VIDEO_ID
- https://www.youtube.com/channel/CHANNEL_ID
- https://www.youtube.com/@USERNAME

### Bilibili
- https://www.bilibili.com/video/BV1234567890
- https://space.bilibili.com/USER_ID
- https://b23.tv/SHORT_CODE

## 示例

分析单个视频：
```
URL: https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

分析UP主频道：
```
URL: https://space.bilibili.com/123456
max_videos: 20
```
