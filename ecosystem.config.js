module.exports = {
  apps: [
    {
      name: "antigravity-bot",
      script: "src/interfaces/telegram/handler.py",
      interpreter: "python3",
      cwd: "/root/antigravity-ai",
      env: {
        PYTHONPATH: "/root/antigravity-ai",
        PYTHONUNBUFFERED: "1"
      },
      watch: false,
      autorestart: true,
      max_restarts: 5,
      restart_delay: 3000
    }
  ]
};
