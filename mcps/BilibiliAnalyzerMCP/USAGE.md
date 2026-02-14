# 使用指南

## 快速开始

### 1. 分析单个视频

**YouTube视频示例**:
```
工具: analyze_video
参数:
  url: https://www.youtube.com/watch?v=dQw4w9WgXcQ
```

**Bilibili视频示例**:
```
工具: analyze_video
参数:
  url: https://www.bilibili.com/video/BV1xx411c7mD
```

### 2. 分析UP主/频道

**YouTube频道示例**:
```
工具: analyze_channel
参数:
  url: https://www.youtube.com/@YouTube
  max_videos: 10
```

**Bilibili UP主示例**:
```
工具: analyze_channel
参数:
  url: https://space.bilibili.com/123456
  max_videos: 15
```

## 输出内容

### 单个视频分析输出
- 平台信息
- 视频标题
- UP主/频道名称
- 上传日期
- 视频时长
- 观看量
- 点赞数
- 视频描述（前500字符）
- 标签（前10个）

### 频道分析输出
- 频道/UP主信息
- 最近视频列表（标题、观看量、时长）
- 总观看量统计
- 平均观看量
- 高频关键词和主题分析

## 注意事项

1. 需要稳定的网络连接
2. 某些视频可能因地区限制无法访问
3. 频道分析可能需要较长时间，建议max_videos不超过20
4. Bilibili短链接(b23.tv)会自动重定向到完整链接
