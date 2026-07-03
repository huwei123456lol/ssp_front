# 简单手机APP前端

这是一个简单的手机APP前端示例，包含任务管理功能。

## 功能特性

- 📱 移动端适配的UI设计
- 📋 任务列表展示
- 📊 今日进度统计
- 🔄 后端API集成
- 🎨 现代化的卡片式布局

## 文件结构

```
├── index.html      # 主页面
├── style.css       # 样式文件
├── app.js          # 前端交互脚本
├── server.js       # 后端API服务器
├── package.json    # 项目配置
└── yangshi.js      # 原始文件
```

## 运行方法

### 1. 安装依赖

```bash
npm install
```

### 2. 启动后端服务器

```bash
npm start
```

服务器将在 http://localhost:3000 启动

### 3. 打开前端页面

在浏览器中打开 `index.html` 文件，或者使用本地服务器：

```bash
# 如果有Python
python -m http.server 8080

# 或者使用其他静态服务器
```

然后访问 http://localhost:8080/index.html

## API接口

- `GET /api/tasks` - 获取任务列表
- `POST /api/tasks` - 创建新任务 (可选)

## 技术栈

- HTML5
- CSS3 (移动端适配)
- JavaScript (ES6+)
- Node.js + Express (后端)

## 浏览器兼容性

支持现代移动浏览器和桌面浏览器。