module.exports = {
  apps: [
    {
      name: "antigravity-bot",
      script: "skills/automation/telegram_handler.py",
      interpreter: "python3",
      cwd: "/root/antigravity-ai",
      env: {
        PYTHONPATH: "/root/antigravity-ai",
        PYTHONUNBUFFERED: "1"
      },
      watch: false,
      autorestart: true,
      max_restarts: 10,
      restart_delay: 2000
    }
  ]
};
