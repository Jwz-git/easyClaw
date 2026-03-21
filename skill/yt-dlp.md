适用系统：macOS/Linux  
触发关键词：yt-dlp、下载视频、下载音频、YouTube、B站、bilibili  
必须流程：  
1) 先读取本技能文件后再生成命令  
2) 默认下载到 "workspace" 目录下的 "videos" 文件夹  
3) URL 必须加双引号，避免特殊字符导致失败  
4) 路径和文件名都要加双引号，避免空格导致失败  
5) 默认不覆盖同名输出文件；若存在先提示用户  
6) 失败时返回错误信息，成功时返回下载完成提示和文件路径
7) 删除下载完成后伴随的m4a文件，保持目录整洁

命令模板：  
- 下载视频（自动选择最佳可用格式）：yt-dlp -o "videos/%(title)s.%(ext)s" "URL"  
- 仅下载音频并转 mp3：yt-dlp -x --audio-format mp3 -o "videos/%(title)s.%(ext)s" "URL"  
- 指定最高 1080p 下载：yt-dlp -f "bv*[height<=1080]+ba/b[height<=1080]" -o "videos/%(title)s.%(ext)s" "URL"  

失败兜底：  
- 若 yt-dlp 不可用，先提示安装（如 macOS 可用 Homebrew 安装）  
- 若 "videos" 目录不存在，先创建目录再下载  
- 若链接不可用或受限，返回失败并说明原因  

约定下载位置： "workspace" 目录下的 "videos" 文件夹，例如输出到 "videos/%(title)s.%(ext)s"。  