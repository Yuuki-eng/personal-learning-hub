# 🎓 Personal Learning Hub - AI智能学习助手

![GitHub stars](https://img.shields.io/github/stars/YOUR_USERNAME/REPO_NAME?style=for-the-badge)
![GitHub forks](https://img.shields.io/github/forks/YOUR_USERNAME/REPO_NAME?style=for-the-badge)
![License](https://img.shields.io/github/license/YOUR_USERNAME/REPO_NAME?style=for-the-badge)
![Version](https://img.shields.io/badge/version-1.0.0-blue?style=for-the-badge)

> 一个集成了AI智能助手、学习计划管理、博客写作、文件管理和音乐播放的全栈学习平台

## ✨ 核心功能

### 🧠 AI智能助手
- **智能对话**：基于DeepSeek API的智能问答系统
- **文档分析**：上传PDF文档，AI帮你总结和分析内容
- **学习建议**：根据你的学习进度提供个性化建议

### 📝 学习管理
- **学习计划**：创建、跟踪和管理学习计划
- **倒计时工具**：专注学习倒计时，提升学习效率
- **博客系统**：Markdown编辑器，记录学习心得

### 🎵 多媒体支持
- **音乐播放器**：集成网易云音乐API，边学习边听音乐
- **歌词显示**：实时显示歌曲歌词
- **音频可视化**：动态音频可视化效果

### 📁 文件管理
- **文档上传**：支持PDF、图片等多种格式
- **智能分类**：自动分类学习资料
- **快速检索**：基于内容的智能搜索

## 🚀 技术栈

### 前端
- **Vue 3** - 渐进式JavaScript框架
- **Element Plus** - UI组件库
- **Vite** - 下一代前端构建工具
- **Tailwind CSS** - 实用优先的CSS框架
- **Pinia** - Vue状态管理

### 后端
- **FastAPI** - 现代、快速的Python Web框架
- **SQLAlchemy** - Python SQL工具包和ORM
- **LangChain** - AI应用开发框架
- **FAISS** - Facebook AI相似性搜索库

### 数据库
- **SQLite** - 轻量级嵌入式数据库
- **ChromaDB** - AI原生向量数据库

### 其他服务
- **网易云音乐API** - 音乐服务接口
- **DeepSeek API** - AI大模型接口

## 📦 快速开始

### 环境要求
- Python 3.8+
- Node.js 16+
- Git

### 1. 克隆项目
```bash
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME
```

### 2. 后端配置
```bash
# 进入后端目录
cd backend

# 创建虚拟环境（Windows）
python -m venv venv
venv\Scripts\activate

# 安装依赖
pip install -r requirements.txt

# 配置环境变量
# 复制.env.example为.env并填写你的API密钥
copy .env.example .env

# 启动后端服务
uvicorn main:app --host 0.0.0.0 --port 8000 --reload
```

### 3. 音乐API服务
```bash
# 进入音乐API目录
cd ../music-api

# 安装依赖
npm install

# 启动服务
node server.js
```

### 4. 前端配置
```bash
# 进入前端目录
cd ../frontend

# 安装依赖
npm install

# 启动开发服务器
npm run dev
```

### 5. 访问应用
- **前端界面**：http://localhost:5173
- **后端API**：http://localhost:8000
- **API文档**：http://localhost:8000/docs
- **音乐API**：http://localhost:3000

## 🎯 项目优势

### 1. 一体化学习体验
- 将学习工具、AI助手、音乐播放整合到一个平台
- 无需在多个应用间切换，提升学习效率

### 2. 智能AI集成
- 基于最新AI技术，提供智能学习建议
- 文档智能分析，快速提取关键信息
- 个性化学习路径推荐

### 3. 现代化技术栈
- 前后端分离架构，易于维护和扩展
- 响应式设计，支持移动端和桌面端
- 模块化开发，代码结构清晰

### 4. 开源免费
- 完全开源，可自由定制和扩展
- 社区驱动，持续更新和改进

## 📸 功能演示

### 主界面
![主界面](docs/images/main-interface.png)

### AI聊天界面
![AI聊天](docs/images/ai-chat.png)

### 学习计划管理
![学习计划](docs/images/study-plan.png)

### 音乐播放器
![音乐播放器](docs/images/music-player.png)

## 🔧 配置说明

### AI服务配置
在 `backend/.env` 文件中配置：
```env
AI_API_KEY=your_deepseek_api_key
AI_API_BASE_URL=https://api.deepseek.com
AI_MODEL_NAME=deepseek-chat
```

### 数据库配置
项目使用SQLite数据库，数据文件位于 `backend/data/app.db`
首次启动会自动创建数据库表结构

### 文件上传配置
- 最大上传文件大小：2GB
- 支持格式：PDF、图片、文本文件等
- 存储路径：`backend/data/uploads/`

## 🤝 贡献指南

我们欢迎所有形式的贡献！以下是参与项目的方式：

### 报告问题
1. 在 [Issues](https://github.com/YOUR_USERNAME/REPO_NAME/issues) 页面查看是否已有类似问题
2. 如果没有，创建新的Issue，描述清晰的问题和复现步骤

### 提交代码
1. Fork 项目到你的账户
2. 创建功能分支 (`git checkout -b feature/amazing-feature`)
3. 提交更改 (`git commit -m 'feat: add amazing feature'`)
4. 推送到分支 (`git push origin feature/amazing-feature`)
5. 创建 Pull Request

### 开发规范
- 遵循现有代码风格
- 添加适当的注释和文档
- 确保代码通过测试
- 更新相关文档

## 📚 相关文档

- [API接口文档](http://localhost:8000/docs)
- [前端组件文档](docs/frontend-components.md)
- [部署指南](docs/deployment-guide.md)
- [开发环境配置](docs/development-setup.md)

## 🐳 Docker部署

### 使用Docker Compose一键部署
```bash
# 克隆项目
git clone https://github.com/YOUR_USERNAME/REPO_NAME.git
cd REPO_NAME

# 启动所有服务
docker-compose up -d
```

### 单独部署服务
```bash
# 构建后端镜像
docker build -t learning-hub-backend -f backend/Dockerfile .

# 构建前端镜像
docker build -t learning-hub-frontend -f frontend/Dockerfile .

# 运行服务
docker run -d -p 8000:8000 learning-hub-backend
docker run -d -p 5173:80 learning-hub-frontend
```

## 📄 许可证

本项目采用 MIT 许可证 - 查看 [LICENSE](LICENSE) 文件了解详情

## 👥 联系方式

- **项目维护者**：[你的名字]
- **邮箱**：[你的邮箱]
- **GitHub**：[@YOUR_USERNAME](https://github.com/YOUR_USERNAME)
- **问题反馈**：[Issues](https://github.com/YOUR_USERNAME/REPO_NAME/issues)

## 🙏 致谢

感谢以下开源项目的支持：
- [FastAPI](https://fastapi.tiangolo.com/)
- [Vue.js](https://vuejs.org/)
- [LangChain](https://www.langchain.com/)
- [Element Plus](https://element-plus.org/)
- [网易云音乐API](https://github.com/Binaryify/NeteaseCloudMusicApi)

---

⭐ **如果这个项目对你有帮助，请给我们一个Star！** ⭐